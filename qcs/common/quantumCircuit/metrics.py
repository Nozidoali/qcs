@property
def num_t(self) -> int:
    return sum(1 for gate in self.gates if gate["name"] in ["T", "Tdg"])

@property
def num_gates(self) -> int:
    return len(self.gates)

@property
def num_2q(self) -> int:
    return sum(1 for gate in self.gates if gate["name"] in ["CNOT", "CZ"])

@property
def num_internal_h(self) -> int:
    first_t: int = next((i for i, gate in enumerate(self.gates) if gate["name"] in ["T", "Tdg"]), len(self.gates))
    last_t: int = len(self.gates) - next((i for i, gate in enumerate(reversed(self.gates)) if gate["name"] in ["T", "Tdg"]), len(self.gates)) if self.num_t > 0 else 0
    return sum(1 for i, gate in enumerate(self.gates) if gate["name"] == "HAD" and first_t <= i < last_t)

@property
def num_h(self) -> int:
    return sum(1 for gate in self.gates if gate["name"] == "HAD")

@property
def first_t(self) -> int:
    return next((i for i, gate in enumerate(self.gates) if gate["name"] in ["T", "Tdg"]), len(self.gates))

@property
def last_t(self) -> int:
    return len(self.gates) - next((i for i, gate in enumerate(reversed(self.gates)) if gate["name"] in ["T", "Tdg"]), len(self.gates)) if self.num_t > 0 else 0

def t_depth_of(self, qubit: int) -> int:
    return sum(1 for gate in self.gates if gate["name"] in ["T", "Tdg"] and gate.get("target") == qubit)

@property
def t_depth(self) -> int:
    if self.num_t == 0:
        return 0
    return max(self.t_depth_of(i) for i in range(self.n_qubits))
