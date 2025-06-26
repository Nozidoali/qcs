#pragma once
#include "circuit.hpp"

namespace core {

// Performs Hadamard gadgetization without external qubit mapping.
// Rewrites internal H gates (between T gates) using ancillae.
QuantumCircuit gadgetize_internal_hadamards(const QuantumCircuit& input);

} // namespace core
