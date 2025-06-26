#pragma once
#include "tableau.hpp"
#include "pauliProduct.hpp"
#include "circuit.hpp"
#include "pauliOptimization.hpp"   // for implement_pauli_* helpers
#include <array>
#include <cstdint>

namespace core {

/**
 * Build a Toffoli (or CCZ) gadget using phase-polynomial tricks.
 *
 * @param tab   tableau to be updated in-place
 * @param cols  three qubit indices {ctrl1, ctrl2, target}
 * @param h_gate  true  → Toffoli (X on target),
 *                false → CCZ      (Z on target)
 *
 * Returns a QuantumCircuit with the generated gates.
 */
QuantumCircuit implement_tof(Tableau& tab,
                             const std::array<std::uint16_t,3>& cols,
                             bool h_gate);

} // namespace core
