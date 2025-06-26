#include "columnMajorTableau.hpp"

namespace core {

/* ---- ctor: initialise stabilizers Zi ---- */
ColumnMajorTableau::ColumnMajorTableau(std::size_t n_qubits)
    : n_(n_qubits), stabs_(n_qubits)
{
    for (std::size_t i = 0; i < n_; ++i) {
        BitVector z(n_); z.xor_bit(i);          // Z_i
        BitVector x(n_);                        // 0
        stabs_[i] = { std::move(z), std::move(x), false };
    }
}

/* ------------------------------------------------------------------ *
 *  Prepend X : flips sign for stabs with Z on qubit q                 *
 * ------------------------------------------------------------------ */
void ColumnMajorTableau::prepend_x(std::size_t q) {
    for (auto& s : stabs_)
        if (s.z.get(q)) s.sign ^= true;
}

/* Prepend Z : flips sign for stabs with X on qubit q */
void ColumnMajorTableau::prepend_z(std::size_t q) {
    for (auto& s : stabs_)
        if (s.x.get(q)) s.sign ^= true;
}

/* Prepend S */
void ColumnMajorTableau::prepend_s(std::size_t q) {
    for (auto& s : stabs_) {
        bool zq = s.z.get(q);
        bool xq = s.x.get(q);
        if (zq && xq) s.sign ^= true;           // phase -i
        if (xq)        s.z.xor_bit(q);          // Z ⊕= X
    }
}

/* Prepend H */
void ColumnMajorTableau::prepend_h(std::size_t q) {
    for (auto& s : stabs_) {
        bool zq = s.z.get(q);
        bool xq = s.x.get(q);
        if (zq && xq) s.sign ^= true;           // phase -i
        if (zq != xq) {                         // swap if different
            s.z.xor_bit(q);
            s.x.xor_bit(q);
        }
    }
}

/* Prepend CX(ctrl,targ) */
void ColumnMajorTableau::prepend_cx(std::size_t ctrl, std::size_t targ) {
    for (auto& s : stabs_) {
        if (s.z.get(ctrl) && s.x.get(targ)) s.sign ^= true;   // phase
        if (s.z.get(targ)) s.z.xor_bit(ctrl);
        if (s.x.get(ctrl)) s.x.xor_bit(targ);
    }
}

/* ------------------------------------------------------------------ *
 *  Convert to row-major RowMajorTableau                                       *
 * ------------------------------------------------------------------ */
RowMajorTableau ColumnMajorTableau::to_row_major() const {
    RowMajorTableau tab(n_);
    for (std::size_t i = 0; i < n_; ++i) {
        PauliProduct p(
            stabs_[i].z,               // already length n_
            stabs_[i].x,
            stabs_[i].sign
        );
        tab.insert_pauli_product(p, i);           // stabilizer
    }
    return tab;
}

} // namespace core
