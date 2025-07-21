def decompose_toffoli(c1: int, c2: int, target: int, clean: bool = False) -> list[dict]:
    gates = []
    gates.append({"name": "HAD", "target": target})
    if clean:
        gates.extend(decompose_ccz_clean_ancilla(c1, c2, target))
    else:
        gates.extend(decompose_ccz_dirty_ancilla(c1, c2, target))
    gates.append({"name": "HAD", "target": target})
    return gates

def decompose_ccz_clean_ancilla(c1: int, c2: int, target: int) -> list[dict]:
    gates = []

    gates.append({"name": "T",    "target": target})
    gates.append({"name": "CNOT", "ctrl": c1, "target": target})
    gates.append({"name": "CNOT", "ctrl": c2, "target": target})
    gates.append({"name": "CNOT", "ctrl": target, "target": c2})
    gates.append({"name": "CNOT", "ctrl": target, "target": c1})
    
    gates.append({"name": "Tdg",  "target": c1})
    gates.append({"name": "Tdg",  "target": c2})
    gates.append({"name": "T",    "target": target})
    
    gates.append({"name": "CNOT", "ctrl": target, "target": c1})
    gates.append({"name": "CNOT", "ctrl": target, "target": c2})
        
    return gates

def decompose_ccz_dirty_ancilla(c1: int, c2: int, target: int) -> list[dict]:
    gates = []
    gates.append({"name": "T",    "target": c1})
    gates.append({"name": "T",    "target": c2})
    gates.append({"name": "T",    "target": target})
    
    gates.append({"name": "CNOT", "ctrl":   c2, "target": c1})
    gates.append({"name": "Tdg",  "target": c1})

    gates.append({"name": "CNOT", "ctrl":   target, "target": c1})
    gates.append({"name": "T",    "target": c1})
    gates.append({"name": "CNOT", "ctrl":   c2, "target": c1})
    gates.append({"name": "Tdg",  "target": c1})

    gates.append({"name": "CNOT", "ctrl":   target, "target": c1})
    gates.append({"name": "CNOT", "ctrl":   target, "target": c2})
    gates.append({"name": "Tdg",  "target": c2})
    gates.append({"name": "CNOT", "ctrl":   target, "target": c2})
    return gates


def is_unique(lst: list) -> bool:
    return len(lst) == len(set(lst))

def add_toffoli(self, c1: int, c2: int, target: int, p1: bool = False, p2: bool = False) -> None:
    assert is_unique([c1, c2, target]), f"Control and target qubits must be unique, got {c1}, {c2}, {target}"
    if p1: self.add_x(c1)
    if p2: self.add_x(c2)   
    self.gates.append({"name": "Tof", "ctrl1": c1, "ctrl2": c2, "target": target})
    if p1: self.add_x(c1)
    if p2: self.add_x(c2)
    
def add_clean_toffoli(self, c1: int, c2: int, target: int) -> None:
    self.add_h(target)
    for gate in decompose_ccz_clean_ancilla(c1, c2, target):
        self.add_gate(gate)
    self.add_h(target)