#include "tOptimizer.hpp"
#include <iostream>
#include <optional>

namespace core {


// Finds a kernel (null-space) vector in a Boolean matrix augmented with extra columns.
// Returns std::nullopt if no new kernel vector is found.
std::optional<BitVector>
kernel(std::vector<BitVector>& mat,
       std::vector<BitVector>& aug,
       std::unordered_map<int,int>& piv /* row → pivot_col */)
{
    const int rows = static_cast<int>(mat.size());
    if (rows == 0) return std::nullopt;

    for (int i = 0; i < rows; ++i) {
        if (piv.count(i)) continue;

        for (auto [row, col] : piv) {
            if (mat[i].get(col)) {
                mat[i].xor_with(mat[row]);      // mat[i] ^= mat[row]
                aug[i].xor_with(aug[row]);      // aug[i] ^= aug[row]
            }
        }

        int idx = mat[i].get_first_one();   // returns −1 if the row is all zeros
        if (idx >= 0 && mat[i].get(idx)) {
            for (auto [row, col] : piv) {
                if (mat[row].get(idx)) {
                    mat[row].xor_with(mat[i]);
                    aug[row].xor_with(aug[i]);
                }
            }
            piv[i] = idx;
        } else {
            return aug[i];                  // Return the corresponding augmented column.
        }
    }
    return std::nullopt;
}

/**
 * @brief  Append pair–interaction bits to every Boolean row.
 *
 * For each input row that begins with the `n_qubits` single-qubit flags
 * (z0 … z(n-1)), this helper appends the upper-triangular list of
 * pairwise ANDs:
 *
 *     z0&z1, z0&z2, …, z(n-2)&z(n-1)
 *
 * Example for `n_qubits = 3`
 * --------------------------
 *   Original row :  [1, 0, 1]
 *   Pair bits     :  z0&z1 = 0,  z0&z2 = 1,  z1&z2 = 0
 *   Result row    :  [1, 0, 1, 0, 1, 0]
 *
 * The number of bits appended to every row is
 * `n_qubits * (n_qubits - 1) / 2`.
 *
 * Complexity
 * ----------
 * • Time   : O(m · n²)  where *m* is `table.size()`  
 * • Memory : Grows each row by the pair-bit count shown above.
 *
 * Parameters
 * ----------
 * table
 *     Original list of BitVectors whose first `n_qubits` bits encode the
 *     Z-mask of each T-gate row.
 * n_qubits
 *     Logical qubit count (also the width of the Z-part in every row).
 *
 * Returns
 * -------
 * A new vector of BitVectors where each row has the extra pair-bits
 * concatenated to its end.
 */
std::vector<BitVector>
extend_boolean_vectors(const std::vector<BitVector>& table, std::size_t n_qubits)
{
    std::vector<BitVector> ext = table;                 // deep copy

    const std::size_t extra_bits = n_qubits * (n_qubits - 1) / 2;

    for (std::size_t row = 0; row < table.size(); ++row) {
        std::vector<bool> extra;  extra.reserve(extra_bits);

        auto z = table[row].get_boolean_vec();          // first n bits
        z.resize(n_qubits);

        /* build upper-triangular products */
        for (std::size_t q = 0; q < n_qubits; ++q)
            for (std::size_t r = q + 1; r < n_qubits; ++r)
                extra.push_back(z[q] && z[r]);          // Zq·Zr

        ext[row].extend_vec(extra);                     // append
    }
    return ext;
}

/* ---------- helper 4 : duplicate / zero-row removal ---------- */
std::vector<std::size_t> to_remove(const std::vector<BitVector>& tab)
{
    std::unordered_map<std::string,int> seen;
    std::vector<std::size_t> erase;
    for (std::size_t i = 0; i < tab.size(); ++i) {
        auto str = tab[i].to_string();
        if (tab[i].popcount() == 0 || seen.count(str))
            erase.push_back(i);
        else
            seen[str] = 1;
    }
    return erase;
}

/* ---------- helper 5 : clear_column (identical to Python) ---------- */
void clear_column(int i,
                    std::vector<BitVector>& matrix,
                    std::vector<BitVector>& augmented,
                    std::unordered_map<int,int>& pivots)
{
    if (!pivots.count(i)) return;
    int val = pivots[i];
    pivots.erase(i);

    if (!augmented[i].get(i)) {
        for (std::size_t j = 0; j < matrix.size(); ++j)
            if (augmented[j].get(i)) {
                pivots[j] = val;
                std::swap(matrix[i],    matrix[j]);
                std::swap(augmented[i], augmented[j]);
                break;
            }
    }
    BitVector col      = matrix[i];
    BitVector aug_col  = augmented[i];

    for (std::size_t j = 0; j < matrix.size(); ++j)
        if (j != static_cast<std::size_t>(i) && augmented[j].get(i)) {
            matrix[j].xor_with(col);
            augmented[j].xor_with(aug_col);
        }
}

std::vector<BitVector>
identity_table(std::size_t n_rows)
{
    std::vector<BitVector> id_table;
    id_table.reserve(n_rows);
    for (std::size_t i = 0; i < n_rows; ++i) {
        BitVector row(n_rows);
        row.xor_bit(i);  // set the i-th bit to 1
        id_table.push_back(row);
    }
    return id_table;
}

template<typename T>
void swap_remove(std::vector<T>& vec, std::size_t pos)
{
    if (pos < vec.size() - 1)         // move last element into the hole
        std::swap(vec[pos], vec.back());
    vec.pop_back();                   // O(1) erase last
}

/*--------------------------------------------------------------------*/
void tohpe(const std::vector<BitVector>& original, std::vector<BitVector>& table, std::size_t n_qubits)
{
    /* Make a writable copy of the incoming table */
    table = original;

    /* Working matrices ------------------------------------------------ */
    auto matrix    = extend_boolean_vectors(table, n_qubits);
    auto augmented = identity_table(table.size());
    std::unordered_map<int,int> pivots;

    /* ========== main optimisation loop ========== */
    while (true) {
        // std::cout << "Matrix:" << std::endl;
        // for (const auto& row : matrix) {
        //     std::cout << row.to_string() << std::endl;
        // }
        // std::cout << "Augmented:" << std::endl;
        // for (const auto& row : augmented) {
        //     std::cout << row.to_string() << std::endl;
        // }

        auto res = kernel(matrix, augmented, pivots);
        if (!res) {
            // No new kernel vector found, optimization is complete.
            break;
        }
        BitVector y = *res;  // the new kernel vector

        // std::cout << "Kernel vector: " << y.to_string() << std::endl;
        // std::cout << "Matrix after:" << std::endl;
        // for (const auto& row : matrix) {
        //     std::cout << row.to_string() << std::endl;
        // }
        // std::cout << "Augmented after:" << std::endl;
        // for (const auto& row : augmented) {
        //     std::cout << row.to_string() << std::endl;
        // }

        /* --------  score potential reductions  -------- */
        std::unordered_map<uint64_t,int> score;
        bool parity = (y.popcount() & 1U) != 0U;
        std::size_t length = table.front().size();  // all rows have same length
        /**
         * First check unary Z
         */
        for (std::size_t i = 0; i < table.size(); ++i) {
            uint64_t key = table[i].to_integer();
            if ((parity && !y.get(i)) || (!parity && y.get(i))) {
                score[key] = 1;        // ← always write 1, no accumulation
            }
        }

        for (std::size_t i = 0; i < table.size(); ++i) {
            if (!y.get(i)) continue;
            for (std::size_t j = 0; j < table.size(); ++j) {
                if (y.get(j)) continue;

                BitVector z = table[i];        // XOR pair (i,j)
                z.xor_with(table[j]);
                uint64_t key = z.to_integer();

                score[key] += 2;               // if key new, default-constructs to 0 then +2
            }
        }

        /* --------  choose best key  -------- */
        uint64_t best_key = 0;
        int      best_val = 0;
        for (auto& [k,v] : score) {

            // std::cout << "z_: " << k << ", Value: " << v << std::endl;
            
            if (v > best_val || (v == best_val && k < best_key)) {
                best_key = k; best_val = v;
            }
        }
            
        if (best_val <= 0) break;
        BitVector z = BitVector::from_integer(best_key, length);
        // std::cout << "z = " << z.to_string() << std::endl;

        /* to_update marks rows affected by the kernel vector y */
        auto to_update = y.get_boolean_vec();                 // length = rows

        /* ---- If y has odd parity, append fresh zero row to all tables -- */
        if (y.popcount() & 1U) {
            table.emplace_back(table.front().size());
            matrix.emplace_back(matrix.front().size());

            BitVector e(table.size()); e.xor_bit(table.size());
            augmented.emplace_back(e);
            to_update.push_back(true);                        // mark new row

            // std::cout << "Matrix after padding:" << std::endl;
            // for (const auto& row : matrix) {
            //     std::cout << row.to_string() << std::endl;
            // }
            // std::cout << "Augmented after padding:" << std::endl;
            // for (const auto& row : augmented) {
            //     std::cout << row.to_string() << std::endl;
            // }
        }

        /* rows to be XOR-updated with z */
        for (std::size_t idx = 0; idx < to_update.size(); ++idx)
            if (to_update[idx]) table[idx].xor_with(z);

        /* -------- remove duplicates / zero rows ---------- */
        auto erase_idx = to_remove(table);
        std::sort(erase_idx.begin(), erase_idx.end(), std::greater<>());

        for (std::size_t i : erase_idx)
        {
            /* Step A -- zero out column i in all matrices before removal   */
            clear_column(static_cast<int>(i), matrix, augmented, pivots);

            /* Step B -- swap_remove on every parallel vector               */
            swap_remove(table,            i);
            swap_remove(matrix,           i);
            swap_remove(augmented,        i);
            swap_remove(to_update,        i);

            std::size_t new_len = table.size();      // length after pop_back

            /* Step C -- pivots bookkeeping                                 *
            * If the row that used to be ‘new_len’ carried a pivot,        *
            * relocate that pivot to row i (now holding the swapped row).  */
            if (auto it = pivots.find(static_cast<int>(new_len)); it != pivots.end())
            {
                int col = it->second;
                pivots.erase(it);
                pivots.emplace(static_cast<int>(i), col);
            }

            /* Step D -- adjust augmented_matrix bits so they match Rust
            *           (Rust toggles bit i and bit new_len in every row). */
            for (std::size_t r = 0; r < augmented.size(); ++r)
            {
                bool bit_i    = augmented[r].get(i);
                bool bit_last = augmented[r].get(new_len);

                if (bit_i != bit_last)              // xor_bit(i) if values differ
                    augmented[r].xor_bit(i);

                if (bit_last)                       // xor_bit(new_len) if that bit is 1
                    augmented[r].xor_bit(new_len);
            }

            /*  Note:  The Rust code leaves column `new_len` in place but zeroed.
                If you want the physical column removed in C++, you could call a
                BitVector method such as erase_bit(new_len) right here.              */
            for (BitVector& bv : table)      bv.erase_bit(new_len);
            for (BitVector& bv : matrix)     bv.erase_bit(new_len);
            for (BitVector& bv : augmented)  bv.erase_bit(new_len);
        }

        /* -------- resynchronise matrix / augmented for affected rows ---- */
        for (std::size_t idx = 0; idx < table.size(); ++idx) {
            if (!to_update[idx]) continue;
            clear_column(static_cast<int>(idx), matrix, augmented, pivots);
            matrix[idx] = table[idx];                  // copy updated row
        }
    }
}


} // namespace core