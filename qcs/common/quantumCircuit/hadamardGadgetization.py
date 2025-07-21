from .base import QuantumCircuit

def hadamard_gadgetization(self, allow_mapping: bool = False) -> QuantumCircuit:
    if allow_mapping:
        return hadamard_gadgetization_mapping(self)
    else:
        return hadamard_gadgetization_no_mapping(self)

def hadamard_gadgetization_no_mapping(self) -> QuantumCircuit:
    initial_circuit = QuantumCircuit()
    initial_circuit.n_qubits = self.n_qubits
    
    internal_circuit = QuantumCircuit()
    internal_circuit.n_qubits = self.n_qubits
    flag = False
    last = max((i for i, gate in enumerate(self.gates) if gate["name"] == "T"), default=0)
    for i, gate in enumerate(self.gates):
        if gate["name"] == "T": flag = True
        if gate["name"] == "HAD" and flag and i < last:
            target = gate["target"]
            _anc = internal_circuit.request_qubit()
            
            initial_circuit.add_gate({"name": "HAD", "target": _anc})
            internal_circuit.add_gate({"name": "S", "target": _anc})
            internal_circuit.add_gate({"name": "S", "target": target})
            internal_circuit.add_gate({"name": "CNOT", "ctrl": target, "target": _anc})
            internal_circuit.add_gate({"name": "S", "target": target})
            internal_circuit.add_gate({"name": "Z", "target": target})
            internal_circuit.add_gate({"name": "CNOT", "ctrl": _anc, "target": target})
            internal_circuit.add_gate({"name": "CNOT", "ctrl": target, "target": _anc})
        else:
            internal_circuit.add_gate(gate)
            
    initial_circuit.append(internal_circuit)
    return initial_circuit

def hadamard_gadgetization_mapping(self) -> 'QuantumCircuit':
    """
    This method allows the hadamard gadgetization with qubit mapping.
    However, the CZ introduced by the gadgetization still requires a Hadamard gate
    """
    _circuit = QuantumCircuit()
    _old_to_new: dict[int, int] = {}
    for i in range(self.n_qubits):
        _old_to_new[i] = _circuit.request_qubit()
        
    def mapped_gate(gate: dict) -> dict:
        new_gate = gate.copy()
        if "ctrl" in gate:
            new_gate["ctrl"] = _old_to_new[gate["ctrl"]]
        if "target" in gate:
            new_gate["target"] = _old_to_new[gate["target"]]
        if "ctrl1" in gate:
            new_gate["ctrl1"] = _old_to_new[gate["ctrl1"]]
        if "ctrl2" in gate:
            new_gate["ctrl2"] = _old_to_new[gate["ctrl2"]]
        return new_gate
        
    flag = False
    last = max((i for i, gate in enumerate(self.gates) if gate["name"] == "T"), default=0)
    for i, gate in enumerate(self.gates):
        if gate["name"] == "T": flag = True
        if gate["name"] == "HAD" and flag and i < last:
            target = gate["target"]
            _anc = _circuit.request_qubit()
            _circuit.add_gate({"name": "HAD", "target": _anc})
            _circuit.add_gate({"name": "CZ", "ctrl": _old_to_new[target], "target": _anc})
            _old_to_new[target] = _anc
        else:
            _mapped_gate = mapped_gate(gate)
            _circuit.add_gate(_mapped_gate)
    return _circuit
