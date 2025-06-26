#pragma once
#include "bitvector.hpp"
#include "tableau.hpp"
#include "circuit.hpp"          // QuantumCircuit
#include <vector>

namespace core {

/**
 * Stores a list of Z-mask rows (phase polynomial) and can:
 *  1.  produce the Clifford correction Tableau
 *  2.  translate itself into a T+CX circuit
 */
class PhasePolynomial {
public:
    explicit PhasePolynomial(std::size_t n_qubits);

    /* add a row (length ≥ n_qubits) */
    void        add_row(const BitVector& row) { table_.push_back(row); }

    /* build Tableau that fixes Clifford phase vs. reference table */
    Tableau     clifford_correction(const std::vector<BitVector>& ref,
                                    std::size_t n_qubits) const;

    /* emit (CX,T) circuit that realises the phase polynomial */
    QuantumCircuit to_circ() const;

    std::size_t n_qubits() const { return n_; }
    const std::vector<BitVector>& rows() const { return table_; }

private:
    std::size_t             n_;
    std::vector<BitVector>  table_;
};

} // namespace core
