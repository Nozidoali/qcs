#include "columnMajorTableau.hpp"
#include <optional>
namespace core {

/* ---- ctor: initialise Z_i stabilizers and X_i destabilizers ---- */
ColumnMajorTableau::ColumnMajorTableau(std::size_t n_qubits)
    : n_(n_qubits), stabs_(n_qubits), destabs_(n_qubits)
{
    for (std::size_t i = 0; i < n_; ++i) {
        BitVector z(n_), x(n_);
        z.xor_bit(i); // Z_i
        stabs_[i] = { z, BitVector(n_), false };

        x.xor_bit(i); // X_i
        destabs_[i] = { BitVector(n_), x, false };
    }
}

/* ---------- Prepend X gate ---------- */
void ColumnMajorTableau::prepend_x(std::size_t q) {
    for (auto& s : stabs_)
        if (s.z.get(q)) s.sign ^= true;

    for (auto& d : destabs_)
        if (d.z.get(q)) d.sign ^= true;
}

/* ---------- Prepend Z gate ---------- */
void ColumnMajorTableau::prepend_z(std::size_t q) {
    for (auto& s : stabs_)
        if (s.x.get(q)) s.sign ^= true;

    for (auto& d : destabs_)
        if (d.x.get(q)) d.sign ^= true;
}

/* ---------- Prepend S gate ---------- */
void ColumnMajorTableau::prepend_s(std::size_t q) {
    for (auto& s : stabs_) {
        bool zq = s.z.get(q), xq = s.x.get(q);
        if (zq && xq) s.sign ^= true;
        if (xq)       s.z.xor_bit(q);
    }

    for (auto& d : destabs_) {
        bool zq = d.z.get(q), xq = d.x.get(q);
        if (zq && xq) d.sign ^= true;
        if (xq)       d.z.xor_bit(q);
    }
}

/* ---------- Prepend H gate ---------- */
void ColumnMajorTableau::prepend_h(std::size_t q) {
    for (auto& s : stabs_) {
        bool zq = s.z.get(q), xq = s.x.get(q);
        if (zq && xq) s.sign ^= true;
        if (zq != xq) { s.z.xor_bit(q); s.x.xor_bit(q); }
    }

    for (auto& d : destabs_) {
        bool zq = d.z.get(q), xq = d.x.get(q);
        if (zq && xq) d.sign ^= true;
        if (zq != xq) { d.z.xor_bit(q); d.x.xor_bit(q); }
    }
}

/* ---------- Prepend CNOT(ctrl, targ) ---------- */
void ColumnMajorTableau::prepend_cx(std::size_t ctrl, std::size_t targ) {
    for (auto& s : stabs_) {
        if (s.z.get(ctrl) && s.x.get(targ)) s.sign ^= true;
        if (s.z.get(targ)) s.z.xor_bit(ctrl);
        if (s.x.get(ctrl)) s.x.xor_bit(targ);
    }

    for (auto& d : destabs_) {
        if (d.z.get(ctrl) && d.x.get(targ)) d.sign ^= true;
        if (d.z.get(targ)) d.z.xor_bit(ctrl);
        if (d.x.get(ctrl)) d.x.xor_bit(targ);
    }
}

/* ------------------------------------------------------------------ *
 *  Convert to row-major RowMajorTableau                                       *
 * ------------------------------------------------------------------ */
RowMajorTableau ColumnMajorTableau::to_row_major() const {
    RowMajorTableau tab(n_);
    for (std::size_t i = 0; i < n_; ++i) {
        PauliProduct p(
            stabs_[i].z,                            // already length n_
            stabs_[i].x,
            stabs_[i].sign
        );
        tab.insert_pauli_product(p, i);             // stabilizer
    }
    return tab;
}

QuantumCircuit ColumnMajorTableau::to_circ(bool inverse) const {
    ColumnMajorTableau tab(*this);  // clone for mutation
    QuantumCircuit qc;
    qc.request_qubits(n_qubits());
    std::size_t n = n_qubits();

    for (std::size_t i = 0; i < n; ++i) {
        // 1. Find pivot stabilizer with X in column i
        std::optional<std::size_t> index_opt;
        for (std::size_t j = 0; j < n; ++j) {
            if (tab.stabilizer(j).x.get(i)) {
                index_opt = j;
                break;
            }
        }

        if (index_opt.has_value()) {
            std::size_t index = index_opt.value();

            // 2. Eliminate other Xs in this column from stabs
            for (std::size_t j = i + 1; j < n; ++j) {
                if (tab.stabilizer(j).x.get(i) && j != index) {
                    tab.prepend_cx(index, j);
                    qc.add_cnot(index, j);
                }
            }

            // 3. Adjust phase if destab has X
            if (tab.destabilizer(index).x.get(i)) {
                tab.prepend_s(index);
                qc.add_s(index);
            }

            // 4. Hadamard to turn X into Z
            tab.prepend_h(index);
            qc.add_h(index);
        }

        // 5. Ensure destab[i].x[i] == 1
        if (!tab.destabilizer(i).x.get(i)) {
            for (std::size_t j = 0; j < n; ++j) {
                if (tab.destabilizer(j).x.get(i)) {
                    tab.prepend_cx(i, j);
                    qc.add_cnot(i, j);
                    break;
                }
            }
        }

        // 6. Clear off-diagonal Xs in destabs
        for (std::size_t j = 0; j < n; ++j) {
            if (tab.destabilizer(j).x.get(i) && j != i) {
                tab.prepend_cx(j, i);
                qc.add_cnot(j, i);
            }
        }

        // 7. Clear off-diagonal Zs in stabs
        for (std::size_t j = 0; j < n; ++j) {
            if (tab.stabilizer(j).z.get(i) && j != i) {
                tab.prepend_cx(i, j);
                qc.add_cnot(i, j);
            }
        }

        // 8. Clear off-diagonal Zs in destabs
        for (std::size_t j = 0; j < n; ++j) {
            if (tab.destabilizer(j).z.get(i) && j != i) {
                tab.prepend_cx(i, j);
                qc.add_cnot(i, j);
                tab.prepend_s(j);
                qc.add_s(j);
                tab.prepend_cx(i, j);
                qc.add_cnot(i, j);
            }
        }

        // 9. Diagonal Z in destab
        if (tab.destabilizer(i).z.get(i)) {
            tab.prepend_s(i);
            qc.add_s(i);
        }

        // 10. Signs
        if (tab.stabilizer(i).sign) {
            tab.prepend_x(i);
            qc.add_x(i);
        }

        if (tab.destabilizer(i).sign) {
            tab.prepend_z(i);
            qc.add_z(i);
        }
    }

    // 11. Handle inverse flag
    if (!inverse) {
        QuantumCircuit out;
        out.request_qubits(n);
        for (auto it = qc.gates.rbegin(); it != qc.gates.rend(); ++it) {
            out.gates.push_back(*it);
            if (it->type() == GateType::S)
                out.add_z(it->qubit1());
        }
        return out;
    }

    std::reverse(qc.gates.begin(), qc.gates.end());
    return qc;
}

} // namespace core
