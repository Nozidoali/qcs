#include "rowMajorTableau.hpp"  // Replace with actual header path
#include <iomanip>
#include <sstream>
#include <iostream>
#include <string>

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
    /* Work on a mutable copy */
    RowMajorTableau tab(*this);
    std::size_t n = n_;

    QuantumCircuit qc;  qc.request_qubits(n);

    std::cout << tab.to_string() << std::endl;

    for (std::size_t i = 0; i < n; ++i) {
        /* ----- Handle Xs in stabiliser rows ----- */
        bool any_x = false;
        std::size_t index = 0;
        for (; index < n; ++index)
            if (tab.x_row(index).get(i)) { any_x = true; break; }

        if (any_x) {
            /* Clear other Xs with CX fan-out (control = index, target = j) */
            for (std::size_t j = i + 1; j < n; ++j)
                if (tab.x_row(j).get(i) && j != index) {

                    std::cout << "Clearing X in stabiliser row " << j
                              << " with control " << index << std::endl;

                    tab.append_cx(index, j);
                    qc.add_cnot(static_cast<std::uint16_t>(index),
                                static_cast<std::uint16_t>(j));
                }

            /* Add S if pivot also has Z */
            if (tab.z_row(index).get(i)) {

                std::cout << "Adding S for stabiliser row " << index
                          << " with pivot " << i << std::endl;

                tab.append_s(index);
                qc.add_s(static_cast<std::uint16_t>(index));
            }

            /* Finally Hadamard on pivot qubit */
            std::cout << "Adding H for stabiliser row " << index
                      << " with pivot " << i << std::endl;

            tab.append_h(index);
            qc.add_h(static_cast<std::uint16_t>(index));
        }

        /* ----- Ensure Z on diagonal (i,i) via CX swap ----- */
        if (!tab.z_row(i).get(i)) {
            std::size_t index2 = i + 1;
            while (index2 < n && !tab.z_row(index2).get(i)) ++index2;
            if (index2 < n) {
                std::cout << "Clearing Z in stabiliser row " << index2
                          << " with control " << i << " by adding CX" 
                          << std::endl;

                tab.append_cx(i, index2);   // control = i, target = index2
                qc.add_cnot(static_cast<std::uint16_t>(i),
                            static_cast<std::uint16_t>(index2));
            }
        }

        /* Clear off-diagonal Zs in stabilisers (control = j, target = i) */
        for (std::size_t j = 0; j < n; ++j)
            if (tab.z_row(j).get(i) && j != i) {

                std::cout << "Clearing Z in stabiliser row " << j
                          << " with control " << i << " by adding CX"
                          << std::endl;

                tab.append_cx(j, i);
                qc.add_cnot(static_cast<std::uint16_t>(j),
                            static_cast<std::uint16_t>(i));
            }

        /* Clear Xs in destabilisers (column i+n) */
        for (std::size_t j = 0; j < n; ++j)
            if (tab.x_row(j).get(i + n) && j != i) {

                std::cout << "Clearing X in destabiliser row " << j
                          << " with control " << i << std::endl;

                tab.append_cx(i, j);        // control = i, target = j
                qc.add_cnot(static_cast<std::uint16_t>(i),
                            static_cast<std::uint16_t>(j));
            }

        /* Handle Zs in destabilisers (column i+n) */
        for (std::size_t j = 0; j < n; ++j)
            if (tab.z_row(j).get(i + n) && j != i) {

                std::cout << "Clearing Z in destabiliser row " << j
                          << " with control " << i << std::endl;

                tab.append_cx(i, j);        // control = i, target = j
                qc.add_cnot(static_cast<std::uint16_t>(i),
                            static_cast<std::uint16_t>(j));

                tab.append_s(j);
                qc.add_s(static_cast<std::uint16_t>(j));

                tab.append_cx(i, j);        // same direction again
                qc.add_cnot(static_cast<std::uint16_t>(i),
                            static_cast<std::uint16_t>(j));
            }

        /* Diagonal S for destabiliser if needed */
        if (tab.z_row(i).get(i + n)) {
            tab.append_s(i);
            qc.add_s(static_cast<std::uint16_t>(i));
        }

        /* Global sign corrections */
        if (tab.sign_bit(i)) {
            tab.append_x(i);
            qc.add_x(static_cast<std::uint16_t>(i));
        }
        if (tab.sign_bit(i + n)) {
            tab.append_z(i);
            qc.add_z(static_cast<std::uint16_t>(i));
        }
    }

    /* If caller wants the inverse circuit instead */
    if (!inverse) {
        QuantumCircuit qc_inv;  qc_inv.request_qubits(n);
        for (auto it = qc.gates.rbegin(); it != qc.gates.rend(); ++it) {
            qc_inv.gates.push_back(*it);
            if (it->type() == GateType::S)          // (S)† = Z · S
                qc_inv.add_z(it->qubit1());
        }
        return qc_inv;
    }
    return qc;
}




} // namespace core
