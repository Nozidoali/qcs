def x_gate(target: int) -> dict:
    return {"name": "X", "target": target}

def h_gate(target: int) -> dict:
    return {"name": "HAD", "target": target}

def s_gate(target: int) -> dict:
    return {"name": "S", "target": target}

def cnot_gate(ctrl: int, target: int) -> dict:
    return {"name": "CNOT", "ctrl": ctrl, "target": target}

def x_gate(target: int) -> dict:
    return {"name": "X", "target": target}

def t_gate(target: int) -> dict:
    return {"name": "T", "target": target}

def t_dagger_gate(target: int) -> dict:
    return {"name": "Tdg", "target": target}

def toffoli_gate(ctrl1: int, ctrl2: int, target: int) -> dict:
    return {"name": "Tof", "ctrl1": ctrl1, "ctrl2": ctrl2, "target": target}

def toffoli_gate_with_ancilla(ctrl1: int, ctrl2: int, target: int) -> list:
    return [
        h_gate(target),
        t_gate(target),
        cnot_gate(ctrl1, target),
        cnot_gate(ctrl2, target),
        cnot_gate(target, ctrl2),
        cnot_gate(target, ctrl1),
        t_dagger_gate(ctrl1),
        t_dagger_gate(ctrl2),
        t_gate(target),
        cnot_gate(target, ctrl1),
        cnot_gate(target, ctrl2),
        h_gate(target),
        s_gate(ctrl1),
    ]

class Circuit:
    def __init__(self):
        self.n_qubits: int = 0
        self.gates: list = []

    def request_qubit(self) -> int:
        self.n_qubits += 1
        return self.n_qubits - 1

    def add_toffoli(
        self, c1: int, c2: int, target: int, p1: bool = False, p2: bool = False, clean: bool = False,
    ) -> None:
        if p1: self.gates.append(x_gate(c1))
        if p2: self.gates.append(x_gate(c2))
        if clean: self.gates.extend(toffoli_gate_with_ancilla(c1, c2, target))
        else: self.gates.append(toffoli_gate(c1, c2, target))
        if p1: self.gates.append(x_gate(c1))
        if p2: self.gates.append(x_gate(c2))

    def add_cnot(self, ctrl: int, target: int, p: bool = False) -> None:
        if p: self.gates.append(x_gate(ctrl))
        self.gates.append(cnot_gate(ctrl, target))
        if p: self.gates.append(x_gate(ctrl))

    def add_x(self, target: int) -> None:
        self.gates.append(x_gate(target))

    def to_qasm(self) -> str:
        qasm_str: str = "OPENQASM 2.0;\n"
        qasm_str += f'include "qelib1.inc";\n'
        qasm_str += f"qreg q[{self.n_qubits}];\n"
        for gate in self.gates:
            if gate["name"] == "Tof":
                qasm_str += f"ccx q[{gate['ctrl1']}], q[{gate['ctrl2']}], q[{gate['target']}];\n"
            elif gate["name"] == "CNOT":
                qasm_str += f"cx q[{gate['ctrl']}], q[{gate['target']}];\n"
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
        return qasm_str

