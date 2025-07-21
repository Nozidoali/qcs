from .base import QuantumCircuit

def optimize_cnot_phase_block(self, gates: list[dict]) -> 'QuantumCircuit':
    from qcs.common.linearFunction import optimize_cnot_phase_block
    optimized_gates = optimize_cnot_phase_block(gates, self.n_qubits)
    print(optimized_gates)
    return optimized_gates

def optimize_cnot_phase_regions(self) -> 'QuantumCircuit':
    _circuit = QuantumCircuit()
    _circuit.request_qubits(self.n_qubits)
    buffer = []
    for gate in self.gates:
        if gate["name"] in {"CNOT", "S", "T", "Tdg", "Z"}:
            buffer.append(gate)
        else:
            if buffer:
                optimized_gates = optimize_cnot_phase_block(self, buffer)
                _circuit.extend(optimized_gates)
                buffer = []
            _circuit.add_gate(gate)
    if buffer:
        optimized_gates = optimize_cnot_phase_block(self, buffer)
        _circuit.extend(optimized_gates)
    return _circuit

def optimize_cnot_regions(self) -> list[dict]:
    gates = self.gates
    out = []
    i = 0
    n = len(gates)

    while i < n:
        g = gates[i]
        if g["name"] == "CNOT":
            tgt = g["target"]
            parity = {}
            order = []
            j = i
            while j < n and gates[j]["name"] == "CNOT" and gates[j]["target"] == tgt:
                ctrl = gates[j]["ctrl"]
                parity[ctrl] = parity.get(ctrl, 0) ^ 1
                if ctrl not in order:
                    order.append(ctrl)
                j += 1
            for ctrl in order:
                if parity[ctrl]:
                    out.append({"name": "CNOT", "ctrl": ctrl, "target": tgt})
            i = j
        else:
            out.append(g)
            i += 1

    _circuit = QuantumCircuit()
    _circuit.n_qubits = self.n_qubits
    _circuit.gates = out
    return _circuit

