#pragma once
#include "circuit.hpp"
#include "columnMajorTableau.hpp"
#include "phasePolynomial.hpp"
#include <string>

namespace core {

/* --------------------------------------------------------------- *
 *  TOptimizer:  single-pass, slice-on-the-fly  T-count optimiser   *
 * --------------------------------------------------------------- */
class TOptimizer {
public:
    explicit TOptimizer(std::size_t n_qubits);

    /* Run optimisation, returning a new circuit  (FastTODD/TOHPE) */
    QuantumCircuit optimize(const QuantumCircuit& circ,
                            const std::string& optimiser = "TOHPE");

private:
    /* helpers */
    bool is_t_gate(const Gate& g) const {
        return g.type() == GateType::T || g.type() == GateType::Td;
    }

    void flush_poly (QuantumCircuit& out);
    void flush_tableau(QuantumCircuit& out);

    /* members */
    std::size_t          n_;
    ColumnMajorTableau   tab_;
    PhasePolynomial      poly_;
    bool                 emitted_poly_sections_{false};

};

void tohpe(const std::vector<BitVector>& table, std::vector<BitVector>& out_table, std::size_t n_qubits);

} // namespace core
