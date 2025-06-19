def is_unique(lst: list) -> bool:
    return len(lst) == len(set(lst))

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

def decompose_toffoli(c1: int, c2: int, target: int, clean: bool = False) -> list[dict]:
    gates = []
    gates.append({"name": "HAD", "target": target})
    if clean:
        gates.extend(decompose_ccz_clean_ancilla(c1, c2, target))
    else:
        gates.extend(decompose_ccz_dirty_ancilla(c1, c2, target))
    gates.append({"name": "HAD", "target": target})
    return gates

class QuantumCircuit:
    def __init__(self):
        self.n_qubits: int = 0
        self.gates: list = []
        
    def to_basic_gates(self) -> 'QuantumCircuit':
        _circuit = QuantumCircuit()
        _circuit.n_qubits = self.n_qubits
        for gate in self.gates:
            assert "name" in gate, f"Gate {gate} does not have a 'name' key"
            if gate["name"] == "Tof":
                _circuit.gates.extend(decompose_toffoli(gate["ctrl1"], gate["ctrl2"], gate["target"]))
            else:
                _circuit.add_gate(gate)
        return _circuit.cleanup_dangling()
    
    def hadamard_gadgetization(self, allow_mapping: bool = False) -> 'QuantumCircuit':
        if allow_mapping:
            return self.hadamard_gadgetization_mapping()
        else:
            return self.hadamard_gadgetization_no_mapping()
    
    def hadamard_gadgetization_no_mapping(self) -> 'QuantumCircuit':
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
    
    def cleanup_dangling(self) -> 'QuantumCircuit':
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

    def request_qubit(self) -> int:
        self.n_qubits += 1
        return self.n_qubits - 1

    def request_qubits(self, n: int) -> list[int]:
        return [self.request_qubit() for _ in range(n)]

    def add_toffoli(self, c1: int, c2: int, target: int, p1: bool = False, p2: bool = False, clean: bool = False) -> None:
        assert is_unique([c1, c2, target]), f"Control and target qubits must be unique, got {c1}, {c2}, {target}"
        if p1: self.add_x(c1)
        if p2: self.add_x(c2)   
        self.gates.append({"name": "Tof", "ctrl1": c1, "ctrl2": c2, "target": target})
        if p1: self.add_x(c1)
        if p2: self.add_x(c2)
    
    def append(self, other: 'QuantumCircuit') -> None:
        assert isinstance(other, QuantumCircuit), "Can only append another QuantumCircuit"
        self.n_qubits = max(self.n_qubits, other.n_qubits)
        self.gates.extend(other.gates)    
            
    def add_gate(self, gate: dict) -> None:
        self.gates.append(gate.copy())
    
    def add_mcx(
        self, cs: list[int], target: int, ps: list[bool] = [], clean: bool = False,
    ) -> None:
        assert len(cs) <= 2, f"MCX only supports 1 or 2 control qubits, got {len(cs)}"
        if len(cs) == 1:
            self.add_cnot(cs[0], target, ps[0])
        elif len(cs) == 2:
            self.add_toffoli(cs[0], cs[1], target, ps[0], ps[1], clean)

    def add_cnot(self, ctrl: int, target: int, p: bool = False) -> None:
        if p: self.add_x(ctrl)
        self.gates.append({"name": "CNOT", "ctrl": ctrl, "target": target})
        if p: self.add_x(ctrl)
        
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
        
    def to_json(self) -> dict:
        return self.gates

    def to_qasm(self, **kwargs) -> str:
        run_zx: bool = kwargs.get("run_zx", False)
        
        qasm_str: str = "OPENQASM 2.0;\n"
        qasm_str += f'include "qelib1.inc";\n'
        qasm_str += f"qreg q[{self.n_qubits}];\n"
        for gate in self.gates:
            if gate["name"] == "Tof":
                qasm_str += f"ccx q[{gate['ctrl1']}], q[{gate['ctrl2']}], q[{gate['target']}];\n"
            elif gate["name"] == "CNOT":
                qasm_str += f"cx q[{gate['ctrl']}], q[{gate['target']}];\n"
            elif gate["name"] == "CZ":
                qasm_str += f"cz q[{gate['ctrl']}], q[{gate['target']}];\n"
            elif gate["name"] == "X":
                qasm_str += f"x q[{gate['target']}];\n"
            elif gate["name"] == "HAD":
                qasm_str += f"h q[{gate['target']}];\n"
            elif gate["name"] == "S":
                qasm_str += f"s q[{gate['target']}];\n"
            elif gate["name"] == "T":
                qasm_str += f"t q[{gate['target']}];\n"
            elif gate["name"] == "Tdg":
                qasm_str += f"tdg q[{gate['target']}];\n"
            else:
                raise NotImplementedError(f"Unsupported gate: {gate['name']}")
        
        if run_zx:
            import pyzx as zx
            circuit = zx.Circuit.from_qasm(qasm_str)
            graph = circuit.to_graph()
            zx.simplify.full_reduce(graph, quiet=True)
            circuit = zx.extract_circuit(graph, up_to_perm=False)
            circuit = circuit.to_basic_gates()
            circuit = circuit.split_phase_gates()
            return circuit.to_qasm()
        return qasm_str
    
    @staticmethod
    def from_zx_circuit(qc) -> 'QuantumCircuit':
        circuit = QuantumCircuit()
        circuit.request_qubits(qc.qubits)
        for gate in qc.gates:
            if gate.name == "Tof":
                circuit.add_toffoli(gate.ctrl1, gate.ctrl2, gate.target)
            elif gate.name == "CCZ":
                circuit.add_h(gate.target)
                circuit.add_toffoli(gate.ctrl1, gate.ctrl2, gate.target)
                circuit.add_h(gate.target)
            elif gate.name == "CNOT":
                circuit.add_cnot(gate.control, gate.target)
            elif gate.name == "NOT":
                circuit.add_x(gate.target)
            elif gate.name == "CZ":
                circuit.add_cz(gate.control, gate.target)
            elif gate.name == "Z":
                circuit.add_z(gate.target)
            elif gate.name == "X":
                circuit.add_x(gate.target)
            elif gate.name == "HAD":
                circuit.add_h(gate.target)
            elif gate.name == "S":
                circuit.add_s(gate.target)
            elif gate.name == "T":
                circuit.add_t(gate.target)
            elif gate.name == "Tdg":
                circuit.add_tdg(gate.target)
            else:
                raise NotImplementedError(f"Unsupported gate: \"{gate.name}\"")
        return circuit
    
    @staticmethod
    def from_file(filename: str) -> 'QuantumCircuit':
        import pyzx as zx
        qc = zx.Circuit.load(filename)
        return QuantumCircuit.from_zx_circuit(qc)
    
    @staticmethod
    def from_qasm(qasm: str) -> 'QuantumCircuit':
        import pyzx as zx
        qc = zx.Circuit.from_qasm(qasm)
        return QuantumCircuit.from_zx_circuit(qc)

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