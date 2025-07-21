from .base import QuantumCircuit

def cleanup_dangling_hadamard(self) -> QuantumCircuit:
    _circuit = QuantumCircuit()
    _circuit.request_qubits(self.n_qubits)
    is_had: dict[int, bool] = {i: False for i in range(self.n_qubits)}
    for i, gate in enumerate(self.gates):
        if gate["name"] == "HAD":
            is_had[gate["target"]] = not is_had[gate["target"]]
        else:
            for j in QuantumCircuit.deps_of(gate):
                if is_had[j]:
                    _circuit.add_gate({"name": "HAD", "target": j})
                    is_had[j] = False
            _circuit.add_gate(gate)
    for j in range(self.n_qubits):
        if is_had[j]:
            _circuit.add_gate({"name": "HAD", "target": j})
            is_had[j] = False
    return _circuit