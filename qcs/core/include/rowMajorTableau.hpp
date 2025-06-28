#pragma once
#include "bitvector.hpp"
#include "pauliProduct.hpp"
#include "circuit.hpp"
#include <vector>

namespace core {

class RowMajorTableau {
public:
    explicit RowMajorTableau(std::size_t n_qubits);
    static RowMajorTableau from_circ(const QuantumCircuit& qc);
    
    /* -------- Clifford append (right-multiply) -------- */
    void append_x (std::size_t q);
    void append_z (std::size_t q);
    void append_v (std::size_t q);
    void append_s (std::size_t q);
    void append_h (std::size_t q);
    void append_cx(std::size_t ctrl, std::size_t targ);
    void append_cz(std::size_t q1,   std::size_t q2);

    /* -------- Clifford prepend (left-multiply) -------- */
    void prepend_x (std::size_t q);
    void prepend_z (std::size_t q);
    void prepend_s (std::size_t q);
    void prepend_h (std::size_t q);
    void prepend_cx(std::size_t ctrl, std::size_t targ);

    /* ---------- NEW lightweight getters ---------- */
    const BitVector& z_row(std::size_t i) const { return z_[i]; }
    const BitVector& x_row(std::size_t i) const { return x_[i]; }
    const BitVector& signs() const { return signs_; }
    bool             sign_bit(std::size_t col) const { return signs_.get(col); }

    /* -------- Pauli extraction / insertion -------- */
    PauliProduct extract_pauli_product(std::size_t col) const;
    void         insert_pauli_product(const PauliProduct& p, std::size_t col);

    /* -------- Accessors -------- */
    std::size_t n_qubits() const { return n_; }

    /* Pretty printer */
    std::string to_string() const;

    /* Build a Clifford + T circuit that realises (or its inverse) this tableau. */
    QuantumCircuit to_circ(bool inverse = false) const;
private:
    std::size_t n_;
    std::vector<BitVector> z_;      // size n_, each length 2n_
    std::vector<BitVector> x_;      // size n_, each length 2n_
    BitVector              signs_;  // length 2n_

    /* helpers */
    static BitVector unit_vector(std::size_t pos, std::size_t len);
};

} // namespace core
