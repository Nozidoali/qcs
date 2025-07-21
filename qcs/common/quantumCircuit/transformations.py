def map_qubit(self, q1: int, q2: int):
    assert 0 <= q1 < self.n_qubits and 0 <= q2 < self.n_qubits, "Qubit indices out of range"
    for gate in self.gates:
        if "ctrl" in gate and gate["ctrl"] == q1:
            gate["ctrl"] = q2
        if "target" in gate and gate["target"] == q1:
            gate["target"] = q2
        if "ctrl1" in gate and gate["ctrl1"] == q1:
            gate["ctrl1"] = q2
        if "ctrl2" in gate and gate["ctrl2"] == q1:
            gate["ctrl2"] = q2
            
def swap_qubits(self, q1: int, q2: int):
    assert 0 <= q1 < self.n_qubits and 0 <= q2 < self.n_qubits, "Qubit indices out of range"
    for gate in self.gates:
        if "ctrl" in gate:
            if gate["ctrl"] == q1:
                gate["ctrl"] = q2
            elif gate["ctrl"] == q2:
                gate["ctrl"] = q1
        if "target" in gate:
            if gate["target"] == q1:
                gate["target"] = q2
            elif gate["target"] == q2:
                gate["target"] = q1
        if "ctrl1" in gate:
            if gate["ctrl1"] == q1:
                gate["ctrl1"] = q2
            elif gate["ctrl1"] == q2:
                gate["ctrl1"] = q1
        if "ctrl2" in gate:
            if gate["ctrl2"] == q1:
                gate["ctrl2"] = q2
            elif gate["ctrl2"] == q2:
                gate["ctrl2"] = q1    