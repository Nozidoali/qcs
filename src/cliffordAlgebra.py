import copy
from quantumCircuit import QuantumCircuit
from dataclasses import dataclass

class BitVector:
    def __init__(self, size=0):
        self.bits = [False] * size

    def __len__(self):
        return len(self.bits)

    @classmethod
    def from_integer_vec(cls, int_vec):
        bv = cls(len(int_vec))
        bv.bits = [bool(v) for v in int_vec]
        return bv

    def size(self):
        return len(self.bits)

    def get(self, index):
        return self.bits[index] if 0 <= index < len(self.bits) else False

    def xor_bit(self, index):
        if 0 <= index < len(self.bits):
            self.bits[index] ^= True

    def xor(self, other):
        for i in range(min(len(self.bits), len(other.bits))):
            self.bits[i] ^= other.bits[i]

    def and_(self, other):
        for i in range(min(len(self.bits), len(other.bits))):
            self.bits[i] &= other.bits[i]

    def negate(self):
        self.bits = [not b for b in self.bits]

    def get_boolean_vec(self):
        return self.bits[:]

    def get_integer_vec(self):
        return [int(b) for b in self.bits]

    def extend_vec(self, vec, nb_qubits):
        """Append additional vector data (bit-wise) to self.bits"""
        self.bits += vec[:]

    def popcount(self):
        return sum(self.bits)

    def get_first_one(self):
        for i, b in enumerate(self.bits):
            if b:
                return i
        return 0  # default to 0 if no '1' found
    
    def get_all_ones(self, nb_bits: int) -> list[int]:
        result = []
        for i in range(min(nb_bits, len(self.bits))):
            if self.bits[i]:
                result.append(i)
        return result

    def __repr__(self):
        return ''.join(['1' if b else '0' for b in self.bits])


class PauliProduct:
    def __init__(self, z, x, sign=False):
        self.z = z  # BitVector
        self.x = x  # BitVector
        self.sign = sign  # bool

    def is_commuting(self, other):
        x1z2 = copy.deepcopy(self.z)
        x1z2.and_(other.x)
        ac = copy.deepcopy(self.x)
        ac.and_(other.z)
        ac.xor(x1z2)
        return ac.popcount() % 2 == 0

    def get_boolean_vec(self, nb_qubits):
        vec_z = self.z.get_boolean_vec()[:nb_qubits]
        vec_x = self.x.get_boolean_vec()[:nb_qubits]
        return vec_z + vec_x

    def pauli_product_mult(self, other):
        x1z2 = copy.deepcopy(self.z)
        x1z2.and_(other.x)
        ac = copy.deepcopy(self.x)
        ac.and_(other.z)
        ac.xor(x1z2)

        self.x.xor(other.x)
        self.z.xor(other.z)

        x1z2 = copy.deepcopy(self.z)
        x1z2.xor(self.x)
        x1z2.xor(other.z)
        x1z2.and_(ac)

        self.sign ^= other.sign ^ (((ac.popcount() + 2 * x1z2.popcount()) % 4) > 1)
        
class Tableau:
    def __init__(self, nb_qubits):
        self.nb_qubits = nb_qubits
        self.z = [self.unit_vector(i, nb_qubits << 1) for i in range(nb_qubits)]
        self.x = [self.unit_vector(i + nb_qubits, nb_qubits << 1) for i in range(nb_qubits)]
        self.signs = BitVector(nb_qubits << 1)

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
        z = BitVector(self.nb_qubits)
        x = BitVector(self.nb_qubits)
        for i in range(self.nb_qubits):
            if self.z[i].get(col): z.xor_bit(i)
            if self.x[i].get(col): x.xor_bit(i)
        return PauliProduct(z, x, self.signs.get(col))

    def insert_pauli_product(self, p, col):
        for i in range(self.nb_qubits):
            if p.z.get(i) != self.z[i].get(col): self.z[i].xor_bit(col)
            if p.x.get(i) != self.x[i].get(col): self.x[i].xor_bit(col)
        if p.sign != self.signs.get(col): self.signs.xor_bit(col)

    def prepend_x(self, qubit): self.signs.xor_bit(qubit)
    def prepend_z(self, qubit): self.signs.xor_bit(qubit + self.nb_qubits)

    def prepend_s(self, qubit):
        stab = self.extract_pauli_product(qubit)
        destab = self.extract_pauli_product(qubit + self.nb_qubits)
        destab.pauli_product_mult(stab)
        self.insert_pauli_product(destab, qubit + self.nb_qubits)

    def prepend_h(self, qubit):
        stab = self.extract_pauli_product(qubit)
        destab = self.extract_pauli_product(qubit + self.nb_qubits)
        self.insert_pauli_product(destab, qubit)
        self.insert_pauli_product(stab, qubit + self.nb_qubits)

    def prepend_cx(self, qubits):
        stab_ctrl = self.extract_pauli_product(qubits[0])
        stab_targ = self.extract_pauli_product(qubits[1])
        destab_ctrl = self.extract_pauli_product(qubits[0] + self.nb_qubits)
        destab_targ = self.extract_pauli_product(qubits[1] + self.nb_qubits)
        stab_targ.pauli_product_mult(stab_ctrl)
        destab_ctrl.pauli_product_mult(destab_targ)
        self.insert_pauli_product(stab_targ, qubits[1])
        self.insert_pauli_product(destab_ctrl, qubits[0] + self.nb_qubits)

    def to_circ(self, inverse: bool):
        tab = copy.deepcopy(self)
        qc = QuantumCircuit()
        qc.request_qubits(self.nb_qubits)
        for i in range(self.nb_qubits):
            if any(x.get(i) for x in tab.x):
                index = next(j for j, x in enumerate(tab.x) if x.get(i))
                for j in range(i + 1, self.nb_qubits):
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
            for j in range(self.nb_qubits):
                if tab.z[j].get(i) and j != i:
                    tab.append_cx([j, i])
                    qc.add_cnot(j, i)
            for j in range(self.nb_qubits):
                if tab.x[j].get(i + self.nb_qubits) and j != i:
                    tab.append_cx([i, j])
                    qc.add_cnot(i, j)
            for j in range(self.nb_qubits):
                if tab.z[j].get(i + self.nb_qubits) and j != i:
                    tab.append_cx([i, j])
                    qc.add_cnot(i, j)
                    tab.append_s(j)
                    qc.add_gate({"name": "S", "target": j})
                    tab.append_cx([i, j])
                    qc.add_cnot(i, j)
            if tab.z[i].get(i + self.nb_qubits):
                tab.append_s(i)
                qc.add_gate({"name": "S", "target": i})
            if tab.signs.get(i):
                tab.append_x(i)
                qc.add_gate({"name": "X", "target": i})
            if tab.signs.get(i + self.nb_qubits):
                tab.append_z(i)
                qc.add_gate({"name": "Z", "target": i})
        if not inverse:
            qc_inv = QuantumCircuit()
            qc_inv.request_qubits(self.nb_qubits)
            for gate in reversed(qc.gates):
                qc_inv.add_gate(gate.copy())
                if gate["name"] == "S":
                    qc_inv.add_gate({"name": "Z", "target": gate["target"]})
            return qc_inv
        return qc
    
@dataclass
class TableauStab:
    z: BitVector
    x: BitVector
    sign: bool = False

class TableauColumnMajor:
    def __init__(self, nb_qubits):
        self.nb_qubits = nb_qubits
        self.stabs = []
        for i in range(nb_qubits):
            z = BitVector(nb_qubits)
            z.xor_bit(i)
            x = BitVector(nb_qubits)
            self.stabs.append(TableauStab(z, x, False))

    def prepend_x(self, qubit):
        for stab in self.stabs:
            if stab.z.get(qubit):
                stab.sign ^= True

    def prepend_z(self, qubit):
        for stab in self.stabs:
            if stab.x.get(qubit):
                stab.sign ^= True

    def prepend_s(self, qubit):
        for stab in self.stabs:
            if stab.z.get(qubit) and stab.x.get(qubit):
                stab.sign ^= True
            if stab.x.get(qubit):
                stab.z.xor_bit(qubit)

    def prepend_h(self, qubit):
        for stab in self.stabs:
            zq, xq = stab.z.get(qubit), stab.x.get(qubit)
            if zq and xq:
                stab.sign ^= True
            # Swap z and x at qubit
            if zq != xq:
                stab.z.xor_bit(qubit)
                stab.x.xor_bit(qubit)

    def prepend_cx(self, qubits):
        ctrl, targ = qubits
        for stab in self.stabs:
            if stab.z.get(ctrl) and stab.x.get(targ):
                stab.sign ^= True
            if stab.z.get(targ):
                stab.z.xor_bit(ctrl)
            if stab.x.get(ctrl):
                stab.x.xor_bit(targ)

    def to_circ(self, inverse=False):
        tab = Tableau(self.nb_qubits)
        for i, stab in enumerate(self.stabs):
            tab.insert_pauli_product(
                PauliProduct(copy.deepcopy(stab.z), copy.deepcopy(stab.x), stab.sign),
                i
            )
        return tab.to_circ(inverse)

class PhasePolynomial:
    def __init__(self, nb_qubits):
        self.nb_qubits = nb_qubits
        self.table = []

    def clifford_correction(self, table, nb_qubits):
        tab = Tableau(nb_qubits)
        for i in range(nb_qubits):
            for j in range(i + 1, nb_qubits):
                z1 = sum(1 for k in range(len(table)) if table[k].get(i) and table[k].get(j))
                z2 = sum(1 for k in range(len(self.table)) if self.table[k].get(i) and self.table[k].get(j))
                diff = ((z1 - z2) % 8 + 8) % 8
                for _ in range(diff // 2):
                    tab.append_cz([i, j])
            z1 = sum(1 for k in range(len(table)) if table[k].get(i))
            z2 = sum(1 for k in range(len(self.table)) if self.table[k].get(i))
            diff = ((z1 - z2) % 8 + 8) % 8
            for _ in range(diff // 2):
                tab.append_s(i)
        return tab

    def to_circ(self):
        qc = QuantumCircuit()
        qc.request_qubits(self.nb_qubits)
        for z in self.table:
            pivot = z.get_first_one()
            indices = z.get_all_ones(self.nb_qubits)
            if pivot in indices:
                indices.remove(pivot)
            for j in indices:
                qc.add_cnot(j, pivot)
            qc.add_t(pivot)
            for j in reversed(indices):
                qc.add_cnot(j, pivot)
        return qc
