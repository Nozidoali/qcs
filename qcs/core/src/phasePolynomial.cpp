#include "phasePolynomial.hpp"
#include <cassert>
#include <iostream>

namespace core {

/* ---- ctor ---- */
PhasePolynomial::PhasePolynomial(std::size_t n_qubits)
    : n_(n_qubits)
{}

void PhasePolynomial::add_row(const BitVector& row) { 
    table_.push_back(row); 
}

const std::vector<BitVector>& PhasePolynomial::rows() const {
    return table_; 
}

std::vector<BitVector>& PhasePolynomial::get_rows() {
    return table_; 
}

std::string PhasePolynomial::to_string() const {
    std::string result;
    for (const auto& row : table_) {
        result += row.to_string() + "\n";
    }
    return result;
}

/* ------------------------------------------------------------------ *
 *  Helper: count rows where bits i & j are both 1                     *
 * ------------------------------------------------------------------ */
static std::size_t count_pair(const std::vector<BitVector>& tbl,
                              std::size_t i, std::size_t j)
{
    std::size_t cnt = 0;
    for (const auto& bv : tbl)
        if (bv.get(i) && bv.get(j)) ++cnt;
    return cnt;
}

/* count rows where bit i is 1 */
static std::size_t count_single(const std::vector<BitVector>& tbl,
                                std::size_t i)
{
    std::size_t cnt = 0;
    for (const auto& bv : tbl)
        if (bv.get(i)) ++cnt;
    return cnt;
}

/* ------------------------------------------------------------------ *
 *  RowMajorTableau correction                                                *
 * ------------------------------------------------------------------ */
RowMajorTableau
PhasePolynomial::clifford_correction(
    const std::vector<BitVector>& ref,
    std::size_t nq) const
{
    assert(nq == n_ && "qubit mismatch");

    RowMajorTableau tab(nq);

    // print table_ and ref for debugging
    for (const auto& row : table_) {
        std::cout << "Phase Polynomial Row: " << row.to_string() << std::endl;
    }

    for (const auto& row : ref) {
        std::cout << "Reference Row: " << row.to_string() << std::endl;
    }

    /* pair-wise CZ phase fix */
    for (std::size_t i = 0; i < nq; ++i) {
        for (std::size_t j = i + 1; j < nq; ++j) {
            std::size_t z1 = count_pair(ref,        i, j);
            std::size_t z2 = count_pair(table_,     i, j);

            std::size_t diff = ((z1 + 8) - z2) & 7U;   // (z1 - z2) mod 8
            for (std::size_t k = 0; k < diff / 2; ++k) {
                std::cout << "Appending CZ for qubits " << i << " and " << j << std::endl;
                tab.append_cz(i, j);
            }
        }

        /* single-qubit S-phase fix */
        std::size_t z1s = count_single(ref,    i);
        std::size_t z2s = count_single(table_, i);
        std::size_t diff = ((z1s + 8) - z2s) & 7U;

        for (std::size_t k = 0; k < diff / 2; ++k) {
            std::cout << "Appending S for qubit " << i << std::endl;
            tab.append_s(i);
        }
    }
    return tab;
}

/* ------------------------------------------------------------------ *
 *  CX+T circuit synthesis                                            *
 * ------------------------------------------------------------------ */
QuantumCircuit PhasePolynomial::to_circ() const {
    QuantumCircuit qc;
    qc.request_qubits(n_);

    for (const BitVector& zmask : table_) {
        std::size_t pivot = zmask.get_first_one();
        if (pivot >= n_) continue;                      // safety

        /* gather controls (excluding pivot) */
        auto ones = zmask.get_all_ones(n_);
        ones.erase(std::remove(ones.begin(), ones.end(), pivot), ones.end());

        /* forward CX fan-in */
        for (std::size_t c : ones) {
            qc.add_cnot(pivot, c);
        }

        qc.add_t(pivot);                               // T gate

        /* uncompute CX fan-in (reverse order) */
        for (auto it = ones.rbegin(); it != ones.rend(); ++it) {
            qc.add_cnot(pivot, *it);
        }
    }
    return qc;
}

bool PhasePolynomial::empty() const {
    return table_.empty();
}

} // namespace core
