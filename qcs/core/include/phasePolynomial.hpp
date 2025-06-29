#pragma once
#include "bitvector.hpp"
#include "rowMajorTableau.hpp"
#include "circuit.hpp"          // QuantumCircuit
#include <vector>

namespace core {

/**
 * Stores a list of Z-mask rows (phase polynomial) and can:
 *  1.  produce the Clifford correction RowMajorTableau
 *  2.  translate itself into a T+CX circuit
 */
class PhasePolynomial {
public:
    explicit PhasePolynomial(std::size_t n_qubits);

    /* add a row (length ≥ n_qubits) */
    void        add_row(const BitVector& row);

    /* build RowMajorTableau that fixes Clifford phase vs. reference table */
    RowMajorTableau     clifford_correction(const std::vector<BitVector>& ref,
                                    std::size_t n_qubits) const;

    /* emit (CX,T) circuit that realises the phase polynomial */
    QuantumCircuit to_circ() const;

    std::size_t n_qubits() const { return n_; }
    const std::vector<BitVector>& rows() const;
    std::vector<BitVector>& get_rows();

    std::string to_string() const;

    bool empty() const;

    std::size_t size() const { return table_.size(); }

private:
    std::size_t             n_;
    std::vector<BitVector>  table_;
};

} // namespace core
