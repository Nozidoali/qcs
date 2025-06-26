#include "tableau.hpp"
#include <algorithm>
#include <sstream>

namespace core {

/* ---- helper: |pos⟩ unit bitvector ---- */
BitVector Tableau::unit_vector(std::size_t pos, std::size_t len) {
    BitVector bv(len);
    bv.xor_bit(pos);
    return bv;
}

/* ---- ctor ---- */
Tableau::Tableau(std::size_t n_qubits)
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

/* ------------------------------------------------------------------ *
 *  Append (gate acts on RHS)                                         *
 * ------------------------------------------------------------------ */
void Tableau::append_x(std::size_t q) { signs_.xor_with(z_[q]); }
void Tableau::append_z(std::size_t q) { signs_.xor_with(x_[q]); }

void Tableau::append_v(std::size_t q) {
    BitVector a = x_[q]; a.negate();
    a.and_with(z_[q]);
    signs_.xor_with(a);
    x_[q].xor_with(z_[q]);
}

void Tableau::append_s(std::size_t q) {
    BitVector a = z_[q];
    a.and_with(x_[q]);
    signs_.xor_with(a);
    z_[q].xor_with(x_[q]);
}

void Tableau::append_h(std::size_t q) {
    append_s(q); append_v(q); append_s(q);
}

void Tableau::append_cx(std::size_t ctrl, std::size_t targ) {
    BitVector a  = z_[ctrl];  a.negate();
    a.xor_with(x_[targ]);
    a.and_with(z_[targ]);
    a.and_with(x_[ctrl]);
    signs_.xor_with(a);

    z_[ctrl].xor_with(z_[targ]);
    x_[targ].xor_with(x_[ctrl]);
}

void Tableau::append_cz(std::size_t q1, std::size_t q2) {
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
PauliProduct Tableau::extract_pauli_product(std::size_t col) const {
    BitVector zmask(n_), xmask(n_);
    for (std::size_t i = 0; i < n_; ++i) {
        if (z_[i].get(col)) zmask.xor_bit(i);
        if (x_[i].get(col)) xmask.xor_bit(i);
    }
    return PauliProduct(std::move(zmask), std::move(xmask), signs_.get(col));
}

void Tableau::insert_pauli_product(const PauliProduct& p, std::size_t col) {
    for (std::size_t i = 0; i < n_; ++i) {
        if (p.z.get(i) != z_[i].get(col)) z_[i].xor_bit(col);
        if (p.x.get(i) != x_[i].get(col)) x_[i].xor_bit(col);
    }
    if (p.sign != signs_.get(col)) signs_.xor_bit(col);
}

/* ------------------------------------------------------------------ *
 *  Prepend (gate acts on LHS)                                        *
 * ------------------------------------------------------------------ */
void Tableau::prepend_x(std::size_t q) { signs_.xor_bit(q); }
void Tableau::prepend_z(std::size_t q) { signs_.xor_bit(q + n_); }

void Tableau::prepend_s(std::size_t q) {
    auto stab   = extract_pauli_product(q);
    auto destab = extract_pauli_product(q + n_);
    destab.pauli_product_mult(stab);
    insert_pauli_product(destab, q + n_);
}

void Tableau::prepend_h(std::size_t q) {
    auto stab   = extract_pauli_product(q);
    auto destab = extract_pauli_product(q + n_);
    insert_pauli_product(destab, q);
    insert_pauli_product(stab,   q + n_);
}

void Tableau::prepend_cx(std::size_t ctrl, std::size_t targ) {
    auto stab_c   = extract_pauli_product(ctrl);
    auto stab_t   = extract_pauli_product(targ);
    auto dest_c   = extract_pauli_product(ctrl + n_);
    auto dest_t   = extract_pauli_product(targ + n_);

    stab_t.pauli_product_mult(stab_c);
    dest_c.pauli_product_mult(dest_t);

    insert_pauli_product(stab_t, targ);
    insert_pauli_product(dest_c, ctrl + n_);
}


/* ----------------------------------------------------------- *
 *  I / X / Y / Z pretty-printer for the tableau                *
 * ----------------------------------------------------------- */
std::string Tableau::to_string() const
{
    const auto pauli_char = [](bool z, bool x) -> char {
        return z ? (x ? 'Y' : 'Z')         // Z=1
                 : (x ? 'X' : 'I');        // Z=0
    };

    std::ostringstream out;

    /* -------- stabiliser rows -------- */
    for (std::size_t i = 0; i < n_; ++i) {
        out << (signs_.get(i) ? '-' : '+') << ' ';
        for (std::size_t j = 0; j < n_; ++j) {
            bool z = z_[i].get(j);
            bool x = x_[i].get(j);
            out << pauli_char(z, x);
        }
        out << '\n';
    }

    /* separator */
    out << std::string(n_ + 2, '-') << '\n';

    /* -------- destabiliser rows -------- */
    for (std::size_t i = 0; i < n_; ++i) {
        out << (signs_.get(n_ + i) ? '-' : '+') << ' ';
        for (std::size_t j = 0; j < n_; ++j) {
            bool z = z_[i].get(n_ + j);
            bool x = x_[i].get(n_ + j);
            out << pauli_char(z, x);
        }
        out << '\n';
    }
    return out.str();
}

/* =========================================================== *
 *  Tableau ➜ QuantumCircuit                                   *
 * =========================================================== */
QuantumCircuit Tableau::to_circ(bool inverse) const
{
    /* Work on a mutable copy */
    Tableau tab(*this);
    std::size_t nq = n_;

    QuantumCircuit qc;  qc.request_qubits(nq);

    for (std::size_t i = 0; i < nq; ++i) {
        /* ----- Handle Xs in stabiliser rows ----- */
        bool any_x = false;
        std::size_t index = 0;
        for (; index < nq; ++index)
            if (tab.x_row(index).get(i)) { any_x = true; break; }

        if (any_x) {
            /* Clear other Xs with CX fan-out */
            for (std::size_t j = i + 1; j < nq; ++j)
                if (tab.x_row(j).get(i) && j != index) {
                    tab.append_cx(index, j);
                    qc.add_cnot(static_cast<std::uint16_t>(index),
                                static_cast<std::uint16_t>(j));
                }

            /* Add S if pivot also has Z */
            if (tab.z_row(index).get(i)) {
                tab.append_s(index);
                qc.add_s(static_cast<std::uint16_t>(index));
            }

            /* Finally Hadamard */
            tab.append_h(index);
            qc.add_h(static_cast<std::uint16_t>(index));
        }

        /* ----- Ensure Z on diagonal i,i via CX swaps ----- */
        if (!tab.z_row(i).get(i)) {
            std::size_t index2 = i + 1;
            while (index2 < nq && !tab.z_row(index2).get(i)) ++index2;
            if (index2 < nq) {
                tab.append_cx(i, index2);
                qc.add_cnot(static_cast<std::uint16_t>(i),
                            static_cast<std::uint16_t>(index2));
            }
        }

        /* Clear off-diagonal Zs in stabilisers */
        for (std::size_t j = 0; j < nq; ++j)
            if (tab.z_row(j).get(i) && j != i) {
                tab.append_cx(j, i);
                qc.add_cnot(static_cast<std::uint16_t>(j),
                            static_cast<std::uint16_t>(i));
            }

        /* Clear Xs in destabilisers (column i+n) */
        for (std::size_t j = 0; j < nq; ++j)
            if (tab.x_row(j).get(i + nq) && j != i) {
                tab.append_cx(i, j);
                qc.add_cnot(static_cast<std::uint16_t>(i),
                            static_cast<std::uint16_t>(j));
            }

        /* Handle Zs in destabilisers (column i+n) */
        for (std::size_t j = 0; j < nq; ++j)
            if (tab.z_row(j).get(i + nq) && j != i) {
                tab.append_cx(i, j);
                qc.add_cnot(static_cast<std::uint16_t>(i),
                            static_cast<std::uint16_t>(j));

                tab.append_s(j);
                qc.add_s(static_cast<std::uint16_t>(j));

                tab.append_cx(i, j);
                qc.add_cnot(static_cast<std::uint16_t>(i),
                            static_cast<std::uint16_t>(j));
            }

        /* Diagonal S for destabiliser if needed */
        if (tab.z_row(i).get(i + nq)) {
            tab.append_s(i);
            qc.add_s(static_cast<std::uint16_t>(i));
        }

        /* Global sign corrections */
        if (tab.sign_bit(i)) {
            tab.append_x(i);
            qc.add_x(static_cast<std::uint16_t>(i));
        }
        if (tab.sign_bit(i + nq)) {
            tab.append_z(i);
            qc.add_z(static_cast<std::uint16_t>(i));
        }
    }

    /* If caller wants the inverse, build qc_inv = qc† */
    if (!inverse) {
        QuantumCircuit qc_inv;  qc_inv.request_qubits(nq);
        for (auto it = qc.gates.rbegin(); it != qc.gates.rend(); ++it) {
            qc_inv.gates.push_back(*it);
            if (it->type() == GateType::S)               // append Z after S in inverse
                qc_inv.add_z(it->qubit1());
        }
        return qc_inv;
    }
    return qc;
}


} // namespace core
