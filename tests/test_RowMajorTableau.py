import pytest
import qcs  # assumes pybind11 bindings are exposed in qcs.core.src.__init__

def test_circuit_to_tableau_and_back(monkeypatch):
    # Step 1: Create a QuantumCircuit
    circuit = qcs.QuantumCircuit()
    circuit.request_qubits(3)
    circuit.add_cnot(0, 1)
    circuit.add_cnot(0, 2)
    circuit.add_cnot(2, 0)
    circuit.add_cnot(2, 1)

    # Step 2: Convert to tableau
    tableau = qcs.to_tableau(circuit)
    assert tableau is not None

    # Step 3: Convert back to a circuit
    circuit_new = qcs.from_tableau(tableau)

    # Step 4: Validate that circuit_new is still a QuantumCircuit with expected gates
    json_data = circuit_new.to_json()

    assert isinstance(json_data, dict)
    assert "circ" in json_data
    assert json_data["circ"] == [
        ["cx", [0, 1]],
        ["cx", [0, 2]],
        ["cx", [2, 0]],
        ["cx", [2, 1]],
    ]
    assert json_data.get("n_qubits") == 3
