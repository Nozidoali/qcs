ALL_AVAILABLE_GATES = [
    # CNOT: Controlled-NOT gate (2-qubit)
    "CNOT",
    # CZ: Controlled-Z gate (2-qubit)
    "CZ",
    # Tof: Toffoli gate (CCX, 3-qubit)
    "Tof",
    # HAD: Hadamard gate (1-qubit)
    "HAD",
    # S: Phase gate (1-qubit)
    "S",
    # T: T gate (pi/8 gate, 1-qubit)
    "T",
    # Tdg: T-dagger gate (inverse T, 1-qubit)
    "Tdg",
    # X: Pauli-X gate (NOT, 1-qubit)
    "X",
    # Z: Pauli-Z gate (1-qubit)
    "Z",
    # CCZ: Controlled-Controlled-Z gate (3-qubit)
    "CCZ",
]

class QuantumCircuit:
    def __init__(self):
        self.n_qubits: int = 0
        self.gates: list = []
        
    def request_qubit(self) -> int:
        self.n_qubits += 1
        return self.n_qubits - 1

    def request_qubits(self, n: int) -> list[int]:
        return [self.request_qubit() for _ in range(n)]
    
    def append(self, other: 'QuantumCircuit') -> None:
        assert isinstance(other, QuantumCircuit), "Can only append another QuantumCircuit"
        self.n_qubits = max(self.n_qubits, other.n_qubits)
        self.gates.extend(other.gates)
        
    def extend(self, gates: list[dict]) -> None:
        for gate in gates:
            self.add_gate(gate)

    def copy(self) -> 'QuantumCircuit':
        new_circuit = QuantumCircuit()
        new_circuit.n_qubits = self.n_qubits
        new_circuit.gates = [{**gate} for gate in self.gates]
        return new_circuit

    def add_gate(self, gate: dict) -> None:
        self.gates.append(gate.copy())

    @staticmethod
    def deps_of(gate: dict) -> set[int]:
        deps: set[int] = set()
        if gate["name"] == "CNOT":
            deps.add(gate["ctrl"])
            deps.add(gate["target"])
        elif gate["name"] == "CZ":
            deps.add(gate["ctrl"])
            deps.add(gate["target"])
        elif gate["name"] == "Tof":
            deps.add(gate["ctrl1"])
            deps.add(gate["ctrl2"])
            deps.add(gate["target"])
        else:
            deps.add(gate["target"])
        return deps
    
    def add_cnot(self, ctrl: int, target: int) -> None:
        self.gates.append({"name": "CNOT", "ctrl": ctrl, "target": target})
        
    def add_cz(self, ctrl: int, target: int) -> None:
        self.gates.append({"name": "CZ", "ctrl": ctrl, "target": target})

    def add_z(self, target: int) -> None:
        self.gates.append({"name": "Z", "target": target})

    def add_x(self, target: int) -> None:
        self.gates.append({"name": "X", "target": target})
        
    def add_h(self, target: int) -> None:
        self.gates.append({"name": "HAD", "target": target})
        
    def add_s(self, target: int) -> None:
        self.gates.append({"name": "S", "target": target})
        
    def add_t(self, target: int) -> None:
        self.gates.append({"name": "T", "target": target})
        
    def add_tdg(self, target: int) -> None:
        self.gates.append({"name": "Tdg", "target": target})
