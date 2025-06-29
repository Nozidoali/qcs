#pragma once
#include "bitvector.hpp"
#include "pauliProduct.hpp"
#include "rowMajorTableau.hpp"          // for conversion in to_row_major()
#include <vector>

namespace core {

class ColumnMajorTableau {
public:
    explicit ColumnMajorTableau(std::size_t n_qubits);

    /* Clifford prepend (acts on LHS) */
    void prepend_x (std::size_t q);
    void prepend_z (std::size_t q);
    void prepend_s (std::size_t q);
    void prepend_h (std::size_t q);
    void prepend_cx(std::size_t ctrl, std::size_t targ);

    /* Conversion helper */
    RowMajorTableau to_row_major() const;
    QuantumCircuit  to_circ(bool inverse) const;

    /* Accessors */
    std::size_t         n_qubits() const { return n_; }
    const PauliProduct& stabilizer(std::size_t q) const { return stabs_[q]; }
    const PauliProduct& destabilizer(std::size_t q) const { return destabs_[q]; }

private:
    std::size_t                     n_;
    std::vector<PauliProduct>       stabs_;   // length n_
    std::vector<PauliProduct>       destabs_; // length 2n_
};

} // namespace core
