from .base import QuantumCircuit
import pyzx as zx

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
    qc = zx.Circuit.load(filename)
    return QuantumCircuit.from_zx_circuit(qc)

@staticmethod
def from_qasm(qasm: str) -> 'QuantumCircuit':
    qc = zx.Circuit.from_qasm(qasm)
    return QuantumCircuit.from_zx_circuit(qc)

@staticmethod
def from_truth_table(truth_table: list[str], n: int, m: int, use_gray_code: bool = True) -> 'QuantumCircuit':
    assert len(truth_table) == m and all(len(tt) == 2 ** n for tt in truth_table)
    qc = QuantumCircuit()
    in_q = qc.request_qubits(n)
    anc = qc.request_qubits(n - 1)
    out_q = qc.request_qubits(m)

    def gray_code(k): return k ^ (k >> 1)
    prev_bits = [0] * n
    seq = range(2 ** n)

    for idx in seq:
        i = gray_code(idx) if use_gray_code else idx
        bits = [int(b) for b in format(i, f"0{n}b")[::-1]]
        flips = [a ^ b for a, b in zip(bits, prev_bits)]
        for j, f in enumerate(flips):
            if f: qc.add_x(in_q[j])
        prev_bits = bits

        work = list(in_q)
        for j in range(n - 1):
            qc.add_toffoli(work[j], work[j + 1], anc[j])
            work[j + 1] = anc[j]

        for k in range(m):
            if truth_table[k][i] == "1":
                qc.add_cnot(work[-1], out_q[k])

        for j in reversed(range(n - 1)):
            qc.add_toffoli(work[j], in_q[j + 1], anc[j])
            work[j + 1] = in_q[j + 1]

    return qc


def to_qc(self, inputs: list = []) -> str:
    qubits = [f"q{i}" for i in range(self.n_qubits)]

    qc_str = f".v {' '.join(qubits)}\n"
    qc_str += f".i {' '.join(inputs) if inputs else ' '.join(qubits)}\n\n"
    qc_str += "BEGIN\n\n"

    for gate in self.gates:
        name = gate["name"]
        if name == "Tof":
            qc_str += f"tof {qubits[gate['ctrl1']]} {qubits[gate['ctrl2']]} {qubits[gate['target']]}\n"
        elif name == "CNOT":
            qc_str += f"tof {qubits[gate['ctrl']]} {qubits[gate['target']]}\n"
        elif name == "CZ":
            qc_str += f"Z {qubits[gate['ctrl']]} {qubits[gate['target']]}\n"
        elif name == "X":
            qc_str += f"X {qubits[gate['target']]}\n"
        elif name == "HAD":
            qc_str += f"H {qubits[gate['target']]}\n"
        elif name == "S":
            qc_str += f"S {qubits[gate['target']]}\n"
        elif name == "T":
            qc_str += f"T {qubits[gate['target']]}\n"
        elif name == "Z":
            qc_str += f"Z {qubits[gate['target']]}\n"
        elif name == "Tdg":
            qc_str += f"T {qubits[gate['target']]}\n"
            qc_str += f"S {qubits[gate['target']]}\n"
            qc_str += f"Z {qubits[gate['target']]}\n"
        else:
            raise NotImplementedError(f"Unsupported gate: {name}")
    qc_str += "\nEND\n"
    return qc_str

def to_json(self) -> dict:
    return self.gates

def to_qasm(self) -> str:
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
        elif gate["name"] == "Z":
            qasm_str += f"z q[{gate['target']}];\n"
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