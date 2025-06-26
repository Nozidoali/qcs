#include "gadgetization.hpp"
#include <algorithm> // for std::max

namespace core {

QuantumCircuit gadgetize_internal_hadamards(const QuantumCircuit& input) {
    QuantumCircuit ancilla_init_circuit(input.n_qubits);
    QuantumCircuit transformed_circuit(input.n_qubits);

    bool encountered_t_gate = false;
    std::size_t last_t_index = 0;

    // Find the index of the last T gate
    for (std::size_t i = 0; i < input.gates.size(); ++i) {
        if (input.gates[i].type() == GateType::T) {
            last_t_index = i;
        }
    }

    for (std::size_t i = 0; i < input.gates.size(); ++i) {
        const Gate& gate = input.gates[i];

        if (gate.type() == GateType::T)
            encountered_t_gate = true;

        if (gate.type() == GateType::H && encountered_t_gate && i < last_t_index) {
            std::uint16_t target = gate.qubit1();
            std::uint16_t ancilla = static_cast<std::uint16_t>(transformed_circuit.request_qubit());

            ancilla_init_circuit.request_qubit();  // ensure consistent qubit_mapping
            ancilla_init_circuit.gates.emplace_back(GateType::H, ancilla);

            transformed_circuit.gates.emplace_back(GateType::S, ancilla);
            transformed_circuit.gates.emplace_back(GateType::S, target);
            transformed_circuit.gates.emplace_back(GateType::CNOT, target, false, ancilla);
            transformed_circuit.gates.emplace_back(GateType::S, target);
            transformed_circuit.gates.emplace_back(GateType::Z, target);
            transformed_circuit.gates.emplace_back(GateType::CNOT, ancilla, false, target);
            transformed_circuit.gates.emplace_back(GateType::CNOT, target, false, ancilla);
        } else {
            transformed_circuit.gates.push_back(gate);
        }
    }

    return ancilla_init_circuit + transformed_circuit;
}

} // namespace core
