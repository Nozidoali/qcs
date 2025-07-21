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

    def add_toffoli(self, c1: int, c2: int, target: int) -> None:
        self.gates.append({"name": "Tof", "ctrl1": c1, "ctrl2": c2, "target": target})
        
    def add_clean_toffoli(self, c1: int, c2: int, target: int) -> None: ...
    
    def num_t(self) -> int: ...
    
    def num_2q(self) -> int: ...
    
    def num_h(self) -> int: ...
    
    def num_internal_h(self) -> int: ...
    
    def t_depth(self) -> int: ...
    
    def t_depth_of(self, qubit: int) -> int: ...
    
    def num_gates(self) -> int: ...
    
    def add_mcx(self, cs: list[int], target: int, ps: list[bool] = [], clean: bool = False) -> None: ...
    
    def to_basic_gates(self) -> 'QuantumCircuit': ...
    
    def gadgetize_toffoli(self) -> 'QuantumCircuit': ...
    
    def hadamard_gadgetization(self, allow_mapping: bool = False) -> 'QuantumCircuit': ...
    
    def optimize_cnot_phase_regions(self) -> 'QuantumCircuit': ...
    
    def optimize_cnot_regions(self) -> 'QuantumCircuit': ...
    
    def cleanup_dangling_hadamard(self) -> 'QuantumCircuit': ...
    
    def cleanup(self) -> 'QuantumCircuit': ...
    
    def to_qasm(self) -> str: ...
    
    def to_qc(self, **kwargs) -> str: ...
    
    def to_json(self) -> dict: ...
    
    @staticmethod
    def from_truth_table(truth_table: list[str], n: int, m: int, use_gray_code: bool = True) -> 'QuantumCircuit': ...
    
    @staticmethod
    def from_qasm(qasm: str) -> 'QuantumCircuit': ...
    
    @staticmethod
    def from_file(filename: str) -> 'QuantumCircuit': ...
    
    def run_zx(self) -> 'QuantumCircuit': ...
    
    def map_qubit(self, q1: int, q2: int): ...
    
    def swap_qubits(self, q1: int, q2: int): ...
    