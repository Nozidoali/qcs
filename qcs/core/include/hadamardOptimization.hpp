#pragma once
#include "rowMajorTableau.hpp"
#include "circuit.hpp"
#include "pauliOptimization.hpp"
#include "toffoliOptimization.hpp"
#include <array>
#include <stdexcept>

namespace core {

    
/**
 * Build a RowMajorTableau representation of any Clifford+T circuit.
 * Non-Clifford gates (T/Td, Toffoli, CCZ) are handled via
 * in-place tableau updates using the same sub-routines used by
 * Hadamard optimisation.
 *
 * @throws runtime_error if an unsupported gate is encountered.
 */
RowMajorTableau tableau_from_circ(const QuantumCircuit& circ);

/* ---------- main optimisation passes ---------- */
QuantumCircuit  internal_h_opt(const QuantumCircuit& c_in);

} // namespace core
