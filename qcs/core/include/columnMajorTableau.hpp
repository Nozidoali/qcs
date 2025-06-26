#pragma once
#include "bitvector.hpp"
#include "pauliProduct.hpp"
#include "tableau.hpp"          // for conversion in to_row_major()
#include <vector>

namespace core {

struct TableauStabilizer {
    BitVector z;   ///< Z mask  (length = n_qubits)
    BitVector x;   ///< X mask  (length = n_qubits)
    bool      sign = false;
};

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
    Tableau to_row_major() const;

    std::size_t n_qubits() const { return n_; }
    const TableauStabilizer& stab(std::size_t q) const { return stabs_[q]; }

private:
    std::size_t                     n_;
    std::vector<TableauStabilizer>  stabs_;   // length n_
};

} // namespace core
