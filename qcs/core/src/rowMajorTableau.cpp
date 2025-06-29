#include "rowMajorTableau.hpp"  // Replace with actual header path
#include <iomanip>
#include <sstream>
#include <iostream>
#include <string>
#include <optional>

namespace core {

/* ---- helper: |pos⟩ unit bitvector ---- */
BitVector RowMajorTableau::unit_vector(std::size_t pos, std::size_t len) {
    BitVector bv(len);
    bv.xor_bit(pos);
    return bv;
}

/* ---- ctor ---- */
RowMajorTableau::RowMajorTableau(std::size_t n_qubits)
    : n_(n_qubits),
      z_(n_qubits),
      x_(n_qubits),
      signs_(n_qubits << 1)
{
    std::size_t len = n_qubits << 1;
    for (std::size_t i = 0; i < n_qubits; ++i) {
        z_[i] = unit_vector(i,           len);
        x_[i] = unit_vector(i + n_qubits, len);
    }
}

/* -------------------------------------------------------------------------
|  Helper to map circuit gates to tableau updates
|  (assumes QuantumCircuit exposes   const std::vector<Gate>& gates()  and
|   Gate has  .kind  and  .qubits[] / .ctrl / .targ  accessors).
|---------------------------------------------------------------------------*/
RowMajorTableau RowMajorTableau::from_circ(const QuantumCircuit& qc)
{
    const std::size_t n = qc.n_qubits;              // whatever accessor you provide
    RowMajorTableau   tab(n);                       // identity tableau

    for (const Gate& g : qc.gates) {

        /* Reject negative controls / targets up-front: */
        if (g.neg1() || g.neg2() || g.neg3())
            throw std::invalid_argument("from_circ: negated controls not supported");

        switch (g.type()) {

        /* ── single-qubit Cliffords ────────────────────────────────────── */
        case GateType::X:  tab.append_x(g.qubit1()); break;
        case GateType::Z:  tab.append_z(g.qubit1()); break;
        case GateType::H:  tab.append_h(g.qubit1()); break;

        case GateType::S:  tab.append_s(g.qubit1()); break;

        /* S† = S³ (tableau update applied three times) */
        case GateType::Sd:
            for (int k = 0; k < 3; ++k) tab.append_s(g.qubit1());
            break;

        /* ── two-qubit Cliffords ───────────────────────────────────────── */
        case GateType::CNOT: {                 // target = q1, control = q2
            tab.append_cx(g.qubit2(), g.qubit1());
            break;
        }

        case GateType::CZ:                     // symmetric
            tab.append_cz(g.qubit1(), g.qubit2());
            break;

        case GateType::Swap: {                 // SWAP = CX ct · CX tc · CX ct
            const auto q1 = g.qubit1();
            const auto q2 = g.qubit2();
            tab.append_cx(q2, q1);
            tab.append_cx(q1, q2);
            tab.append_cx(q2, q1);
            break;
        }

        /* ── unsupported (non-Clifford) gates ─────────────────────────── */
        default:
            throw std::invalid_argument(
                "from_circ: non-Clifford gate encountered (" +
                gate_type_to_string(g.type()) + ')');
        }
    }
    return tab;
}

/* ------------------------------------------------------------------ *
 *  Append (gate acts on RHS)                                         *
 * ------------------------------------------------------------------ */
void RowMajorTableau::append_x(std::size_t q) { signs_.xor_with(z_[q]); }
void RowMajorTableau::append_z(std::size_t q) { signs_.xor_with(x_[q]); }

void RowMajorTableau::append_v(std::size_t q) {
    // V gate: Z → Y = iXZ → flip sign when X=0 and Z=1
    BitVector a = x_[q]; 
    a.negate();                      // a = ~x
    a.and_with(z_[q]);              // a = ~x & z
    signs_.xor_with(a);             // flip sign where Z-only
    x_[q].xor_with(z_[q]);          // X ← X ⊕ Z
}

void RowMajorTableau::append_s(std::size_t q) {
    BitVector a = z_[q];
    a.and_with(x_[q]);
    signs_.xor_with(a);
    z_[q].xor_with(x_[q]);
}

void RowMajorTableau::append_h(std::size_t q) {
    // append_s(q); append_v(q); append_s(q); // H = S·V·S
    BitVector& x = x_[q];
    BitVector& z = z_[q];

    BitVector y_mask = x;      // Y = X & Z
    y_mask.and_with(z);
    signs_.xor_with(y_mask);   // flip sign if originally Y

    x.swap_with(z);            // X ↔ Z
}

void RowMajorTableau::append_cx(std::size_t ctrl, std::size_t targ) {
    BitVector a  = z_[ctrl];  a.negate();
    a.xor_with(x_[targ]);
    a.and_with(z_[targ]);
    a.and_with(x_[ctrl]);
    signs_.xor_with(a);

    z_[ctrl].xor_with(z_[targ]);
    x_[targ].xor_with(x_[ctrl]);
}

void RowMajorTableau::append_cz(std::size_t q1, std::size_t q2) {
    // this could be done easier
    append_s(q1);
    append_s(q2);
    append_cx(q1, q2);
    append_s(q2);
    append_z(q2);
    append_cx(q1, q2);
}

/* ------------------------------------------------------------------ *
 *  Extract / insert Pauli products                                   *
 * ------------------------------------------------------------------ */
PauliProduct RowMajorTableau::extract_pauli_product(std::size_t col) const {
    BitVector zmask(n_), xmask(n_);
    for (std::size_t i = 0; i < n_; ++i) {
        if (z_[i].get(col)) zmask.xor_bit(i);
        if (x_[i].get(col)) xmask.xor_bit(i);
    }
    return PauliProduct(std::move(zmask), std::move(xmask), signs_.get(col));
}

void RowMajorTableau::insert_pauli_product(const PauliProduct& p, std::size_t col) {
    for (std::size_t i = 0; i < n_; ++i) {
        if (p.z.get(i) != z_[i].get(col)) z_[i].xor_bit(col);
        if (p.x.get(i) != x_[i].get(col)) x_[i].xor_bit(col);
    }
    if (p.sign != signs_.get(col)) signs_.xor_bit(col);
}

/* ------------------------------------------------------------------ *
 *  Prepend (gate acts on LHS)                                        *
 * ------------------------------------------------------------------ */
void RowMajorTableau::prepend_x(std::size_t q) { signs_.xor_bit(q); }
void RowMajorTableau::prepend_z(std::size_t q) { signs_.xor_bit(q + n_); }

void RowMajorTableau::prepend_s(std::size_t q) {
    auto stabilizer   = extract_pauli_product(q);
    auto destab = extract_pauli_product(q + n_);
    destab.pauli_product_mult(stabilizer);
    insert_pauli_product(destab, q + n_);
}

void RowMajorTableau::prepend_h(std::size_t q) {
    auto stabilizer   = extract_pauli_product(q);
    auto destab = extract_pauli_product(q + n_);
    insert_pauli_product(destab, q);
    insert_pauli_product(stabilizer,   q + n_);
}

void RowMajorTableau::prepend_cx(std::size_t ctrl, std::size_t targ) {
    auto stab_c   = extract_pauli_product(ctrl);
    auto stab_t   = extract_pauli_product(targ);
    auto dest_c   = extract_pauli_product(ctrl + n_);
    auto dest_t   = extract_pauli_product(targ + n_);

    stab_t.pauli_product_mult(stab_c);
    dest_c.pauli_product_mult(dest_t);

    insert_pauli_product(stab_t, targ);
    insert_pauli_product(dest_c, ctrl + n_);
}

std::string RowMajorTableau::to_string() const
{
    const auto pauli_char = [](bool z, bool x) -> char {
        return z ? (x ? 'Y' : 'Z')         // Z=1
                 : (x ? 'X' : 'I');        // Z=0
    };

    std::ostringstream out;

    out << "Row-major stabiliser tableau (Aaronson-Gottesman encoding)\n";
    out << "n_qubits = " << n_ << "\n";
    out << "Rows  |  Sign  |  Pauli String\n";
    out << "------+--------+----------------\n";
    
    // Stabiliser rows (indices 0..n-1)
    for (std::size_t i = 0; i < n_; ++i) {
        out << ' ' << std::setw(3) << i << "  |   "
        << (signs_.get(i) ? '-' : '+') << "    |  ";
        for (std::size_t j = 0; j < n_; ++j) {
            out << pauli_char(z_[j].get(i), x_[j].get(i));
        }
        out << '\n';
    }

    // Separator line
    out << "------+--------+----------------\n";

    // Destabiliser rows (indices n..2n-1)
    for (std::size_t i = 0; i < n_; ++i) {
        std::size_t idx = n_ + i;
        out << ' ' << std::setw(3) << idx << "  |   "
            << (signs_.get(idx) ? '-' : '+') << "    |  ";
        for (std::size_t j = 0; j < n_; ++j) {
            out << pauli_char(z_[j].get(idx), x_[j].get(idx));
        }
        out << '\n';
    }

    return out.str();
}

/* =========================================================== *
 *  RowMajorTableau ➜ QuantumCircuit                                   *
 * =========================================================== */
QuantumCircuit RowMajorTableau::to_circ(bool inverse) const
{
    RowMajorTableau tab(*this);
    std::size_t n = tab.n_qubits();

    QuantumCircuit qc;
    qc.request_qubits(n);

    std::cout << tab.to_string() << '\n';

    for (std::size_t i = 0; i < n; ++i) {

        // std::cout << "Processing qubit " << i << ":\n";
        // std::cout << "Stabilizer X: " << tab.x_row(i).to_string() << '\n';
        // std::cout << "Stabilizer Z: " << tab.z_row(i).to_string() << '\n';

        // std::cout << "Stabilizer X bit len = " << tab.x_row(i).size() << '\n';
        // std::cout << "Stabilizer Z bit len = " << tab.z_row(i).size() << '\n';

        // Step 1: Find pivot in stabilizer X matrix
        std::optional<std::size_t> index_opt;
        for (std::size_t j = 0; j < n; ++j) {
            if (tab.x_row(j).get(i)) {
                index_opt = j;
                break;
            }
        }

        // std::cout << "Find pivot index for stabilizer X at qubit " << i << ": ";
        // std::cout << (index_opt.has_value() ? std::to_string(index_opt.value()) : "none") << '\n';

        if (index_opt.has_value()) {
            std::size_t index = index_opt.value();

            // Step 2: Clear other Xs in stabilizers
            for (std::size_t j = i + 1; j < n; ++j) {
                if (tab.x_row(j).get(i) && j != index) {
                    tab.append_cx(index, j);
                    qc.add_cnot(index, j);
                }
            }

            // Step 3: If pivot also has Z, apply S
            if (tab.z_row(index).get(i)) {
                tab.append_s(index);
                qc.add_s(index);
            }

            // std::cout << "Applying H to qubit " << index << ":\n";

            // Step 4: Apply H
            tab.append_h(index);
            qc.add_h(index);
        }

        // Step 5: Ensure Z on (i, i)
        if (!tab.z_row(i).get(i)) {

            std::cout << "Z pivot missing at qubit " << i << std::endl;
            
            std::size_t z_pivot = i + 1;
            while (z_pivot < n && !tab.z_row(z_pivot).get(i)) ++z_pivot;
            if (z_pivot < n) {
                tab.append_cx(i, z_pivot);
                qc.add_cnot(i, z_pivot);
            }
            std::cout << "Adding CNOT ctrl=" << i << " target=" << z_pivot << std::endl;
        }

        // Step 6: Clear off-diagonal Zs in stabilizers
        for (std::size_t j = 0; j < n; ++j) {
            if (tab.z_row(j).get(i) && j != i) {

                std::cout << "Clearing off-diagonal Z at qubit " << j << " for stabilizer " << i << std::endl;

                tab.append_cx(j, i);
                qc.add_cnot(j, i);
            }
        }

        // Step 7: Clear off-diagonal Xs in destabilisers (column i+n)
        for (std::size_t j = 0; j < n; ++j) {
            if (tab.x_row(j).get(i + n) && j != i) {

                std::cout << "Clearing off-diagonal X at qubit " << j << " for destabilisers " << i + n << std::endl;

                tab.append_cx(i, j);
                qc.add_cnot(i, j);
            }
        }
        
        // Step 8: Clear off-diagonal Zs in destabilisers (column i+n)
        for (std::size_t j = 0; j < n; ++j) {
            if (tab.z_row(j).get(i + n) && j != i) {

                std::cout << "Clearing off-diagonal Z at qubit " << j << " for destabilisers " << i + n << std::endl;

                tab.append_cx(i, j);
                qc.add_cnot(i, j);
                tab.append_s(j);
                qc.add_s(j);
                tab.append_cx(i, j);
                qc.add_cnot(i, j);
            }
        }
        
        // Step 9: Apply diagonal S if needed in destabiliser
        if (tab.z_row(i).get(i + n)) {

            std::cout << "Applying S to destabilisers at qubit " << i + n << std::endl;

            tab.append_s(i);
            qc.add_s(i);
        }

        // Step 10: Sign corrections
        if (tab.sign_bit(i)) {

            std::cout << "Applying X to qubit " << i << " due to sign correction\n";

            tab.append_x(i);
            qc.add_x(i);
        }
        if (tab.sign_bit(i + n)) {

            std::cout << "Applying Z to qubit " << i << " due to sign correction\n";

            tab.append_z(i);
            qc.add_z(i);
        }

        std::cout << "After processing qubit " << i << ":\n";
        std::cout << qc.to_string() << '\n';
        std::cout << tab.to_string() << '\n';
    }

    std::cout << "Final tableau:\n" << tab.to_string() << '\n';

    // Step 11: Reverse + add Z if !inverse
    if (!inverse) {
        QuantumCircuit out; out.request_qubits(n);
        for (auto it = qc.gates.rbegin(); it != qc.gates.rend(); ++it) {
            out.gates.push_back(*it);
            if (it->type() == GateType::S)
                out.add_z(it->qubit1());
        }
        return out;
    }

    return qc;
}

} // namespace core
