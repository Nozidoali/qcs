#pragma once
#include "rowMajorTableau.hpp"
#include "pauliProduct.hpp"
#include "circuit.hpp"
#include <cstdint>

namespace core {

/* Z-rotation from an explicit PauliProduct (length ≥ n_qubits) */
QuantumCircuit implement_pauli_z_rotation_from_pauli_product(
        const RowMajorTableau& tab,            // read-only (pivot search only)
        const PauliProduct& p);

/* Z-rotation described by tableau column  col  (does not mutate tableau) */
QuantumCircuit implement_pauli_z_rotation(
        const RowMajorTableau& tab,
        std::size_t col);

/* Full Pauli rotation of tableau column  col .
 *   – mutates  tab  via CX/S/H calls to bring it to Z-form
 *   – returns circuit realising rotation */
QuantumCircuit implement_pauli_rotation(
        RowMajorTableau& tab,
        std::size_t col);

} // namespace core
