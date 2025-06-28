# simple_tableau.py
from __future__ import annotations
import copy

from .bitVector import BitVector
from .pauliProduct import PauliProduct
from .quantumCircuit import QuantumCircuit

class RowMajorTableau:
    """
    Row-major stabiliser tableau (Aaronson-Gottesman encoding).
    
    Reference: https://www.scottaaronson.com/papers/chp6.pdf
    """
    def __init__(self, n_qubits):
        self.n_qubits = n_qubits
        self.z = [self.unit_vector(i, n_qubits << 1) for i in range(n_qubits)]
        self.x = [self.unit_vector(i + n_qubits, n_qubits << 1) for i in range(n_qubits)]
        self.signs = BitVector(n_qubits << 1)

    @staticmethod
    def unit_vector(pos, size):
        bv = BitVector(size)
        bv.xor_bit(pos)
        return bv

    def append_x(self, qubit): self.signs.xor(self.z[qubit])
    def append_z(self, qubit): self.signs.xor(self.x[qubit])

    def append_v(self, qubit):
        a = copy.deepcopy(self.x[qubit])
        a.negate()
        a.and_(self.z[qubit])
        self.signs.xor(a)
        self.x[qubit].xor(self.z[qubit])

    def append_s(self, qubit):
        a = copy.deepcopy(self.z[qubit])
        a.and_(self.x[qubit])
        self.signs.xor(a)
        self.z[qubit].xor(self.x[qubit])

    def append_h(self, qubit):
        self.append_s(qubit)
        self.append_v(qubit)
        self.append_s(qubit)

    def append_cx(self, qubits):
        a = copy.deepcopy(self.z[qubits[0]])
        a.negate()
        a.xor(self.x[qubits[1]])
        a.and_(self.z[qubits[1]])
        a.and_(self.x[qubits[0]])
        self.signs.xor(a)
        self.z[qubits[0]].xor(self.z[qubits[1]])
        self.x[qubits[1]].xor(self.x[qubits[0]])

    def append_cz(self, qubits):
        self.append_s(qubits[0])
        self.append_s(qubits[1])
        self.append_cx(qubits)
        self.append_s(qubits[1])
        self.append_z(qubits[1])
        self.append_cx(qubits)

    def extract_pauli_product(self, col):
        z = BitVector(self.n_qubits)
        x = BitVector(self.n_qubits)
        for i in range(self.n_qubits):
            if self.z[i].get(col): z.xor_bit(i)
            if self.x[i].get(col): x.xor_bit(i)
        return PauliProduct(z, x, self.signs.get(col))

    def insert_pauli_product(self, p, col):
        for i in range(self.n_qubits):
            if p.z.get(i) != self.z[i].get(col): self.z[i].xor_bit(col)
            if p.x.get(i) != self.x[i].get(col): self.x[i].xor_bit(col)
        if p.sign != self.signs.get(col): self.signs.xor_bit(col)

    def prepend_x(self, qubit): self.signs.xor_bit(qubit)
    def prepend_z(self, qubit): self.signs.xor_bit(qubit + self.n_qubits)

    def prepend_s(self, qubit):
        stabilizer = self.extract_pauli_product(qubit)
        destab = self.extract_pauli_product(qubit + self.n_qubits)
        destab.pauli_product_mult(stabilizer)
        self.insert_pauli_product(destab, qubit + self.n_qubits)

    def prepend_h(self, qubit):
        stabilizer = self.extract_pauli_product(qubit)
        destab = self.extract_pauli_product(qubit + self.n_qubits)
        self.insert_pauli_product(destab, qubit)
        self.insert_pauli_product(stabilizer, qubit + self.n_qubits)

    def prepend_cx(self, qubits):
        stab_ctrl = self.extract_pauli_product(qubits[0])
        stab_targ = self.extract_pauli_product(qubits[1])
        destab_ctrl = self.extract_pauli_product(qubits[0] + self.n_qubits)
        destab_targ = self.extract_pauli_product(qubits[1] + self.n_qubits)
        stab_targ.pauli_product_mult(stab_ctrl)
        destab_ctrl.pauli_product_mult(destab_targ)
        self.insert_pauli_product(stab_targ, qubits[1])
        self.insert_pauli_product(destab_ctrl, qubits[0] + self.n_qubits)

    def to_circ(self, inverse: bool):
        tab = copy.deepcopy(self)
        qc = QuantumCircuit()
        qc.request_qubits(self.n_qubits)
        for i in range(self.n_qubits):
            if any(x.get(i) for x in tab.x):
                index = next(j for j, x in enumerate(tab.x) if x.get(i))
                for j in range(i + 1, self.n_qubits):
                    if tab.x[j].get(i) and j != index:
                        tab.append_cx([index, j])
                        qc.add_cnot(ctrl=index, target=j)
                if tab.z[index].get(i):
                    tab.append_s(index)
                    qc.add_gate({"name": "S", "target": index})
                tab.append_h(index)
                qc.add_gate({"name": "HAD", "target": index})
            if not tab.z[i].get(i):
                index = next(j for j, z in enumerate(tab.z) if z.get(i))
                tab.append_cx([i, index])
                qc.add_cnot(i, index)
            for j in range(self.n_qubits):
                if tab.z[j].get(i) and j != i:
                    tab.append_cx([j, i])
                    qc.add_cnot(j, i)
            for j in range(self.n_qubits):
                if tab.x[j].get(i + self.n_qubits) and j != i:
                    tab.append_cx([i, j])
                    qc.add_cnot(i, j)
            for j in range(self.n_qubits):
                if tab.z[j].get(i + self.n_qubits) and j != i:
                    tab.append_cx([i, j])
                    qc.add_cnot(i, j)
                    tab.append_s(j)
                    qc.add_gate({"name": "S", "target": j})
                    tab.append_cx([i, j])
                    qc.add_cnot(i, j)
            if tab.z[i].get(i + self.n_qubits):
                tab.append_s(i)
                qc.add_gate({"name": "S", "target": i})
            if tab.signs.get(i):
                tab.append_x(i)
                qc.add_gate({"name": "X", "target": i})
            if tab.signs.get(i + self.n_qubits):
                tab.append_z(i)
                qc.add_gate({"name": "Z", "target": i})
        if not inverse:
            qc_inv = QuantumCircuit()
            qc_inv.request_qubits(self.n_qubits)
            for gate in reversed(qc.gates):
                qc_inv.add_gate(gate.copy())
                if gate["name"] == "S":
                    qc_inv.add_gate({"name": "Z", "target": gate["target"]})
            return qc_inv
        return qc

    def __str__(self) -> str:
        """
        Pretty-print the stabilizer tableau in row-major form.
        Uses Aaronson-Gottesman encoding.
        Displays 2n generators (destabilizers and stabilizers) as Pauli strings.
        """
        def pauli_char(z, x):
            if not z and not x: return 'I'
            if not z and x:     return 'X'
            if z and not x:     return 'Z'
            return 'Y'

        header = f"Row-major stabiliser tableau (Aaronson-Gottesman encoding)\n"
        header += f"n_qubits = {self.n_qubits}\n"
        header += "Rows  |  Sign  |  Pauli String\n"
        header += "------+--------+----------------\n"

        lines = []
        for row in range(2 * self.n_qubits):
            if row == self.n_qubits:
                lines.append("------+--------+----------------")
            sign = '-' if self.signs.get(row) else '+'
            paulis = []
            for col in range(self.n_qubits):
                z_bit = self.z[col].get(row)
                x_bit = self.x[col].get(row)
                paulis.append(pauli_char(z_bit, x_bit))
            lines.append(f"{row:>4}  |   {sign}    |  " + "".join(paulis))

        return header + "\n".join(lines)