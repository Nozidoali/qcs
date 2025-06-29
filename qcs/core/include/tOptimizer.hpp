#pragma once
#include "circuit.hpp"
#include "columnMajorTableau.hpp"
#include "phasePolynomial.hpp"
#include <string>

namespace core {

QuantumCircuit optimize_t_gates(const QuantumCircuit& circ);
void tohpe(const std::vector<BitVector>& table, std::vector<BitVector>& out_table, std::size_t n_qubits);

} // namespace core
