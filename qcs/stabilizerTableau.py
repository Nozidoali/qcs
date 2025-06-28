import copy
from .common import QuantumCircuit
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

    def extend_vec(self, vec, n_qubits):
        """Append additional vector data (bit-wise) to self.bits"""
        self.bits += vec[:]

    def popcount(self):
        return sum(self.bits)

    def get_first_one(self):
        try:
            return self.bits.index(True)
        except ValueError:
            return 0 # Return 0 if no '1' is found, as a default behavior
    
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

    def get_boolean_vec(self, n_qubits):
        vec_z = self.z.get_boolean_vec()[:n_qubits]
        vec_x = self.x.get_boolean_vec()[:n_qubits]
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
        
class RowMajorTableau:
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
    
@dataclass
class TableauStabilizer:
    z: BitVector
    x: BitVector
    sign: bool = False

class ColumnMajorTableau:
    def __init__(self, n_qubits):
        self.n_qubits = n_qubits
        self.stabs = []
        for i in range(n_qubits):
            z = BitVector(n_qubits)
            z.xor_bit(i)
            x = BitVector(n_qubits)
            self.stabs.append(TableauStabilizer(z, x, False))

    def prepend_x(self, qubit):
        for stabilizer in self.stabs:
            if stabilizer.z.get(qubit):
                stabilizer.sign ^= True

    def prepend_z(self, qubit):
        for stabilizer in self.stabs:
            if stabilizer.x.get(qubit):
                stabilizer.sign ^= True

    def prepend_s(self, qubit):
        for stabilizer in self.stabs:
            if stabilizer.z.get(qubit) and stabilizer.x.get(qubit):
                stabilizer.sign ^= True
            if stabilizer.x.get(qubit):
                stabilizer.z.xor_bit(qubit)

    def prepend_h(self, qubit):
        for stabilizer in self.stabs:
            zq, xq = stabilizer.z.get(qubit), stabilizer.x.get(qubit)
            if zq and xq:
                stabilizer.sign ^= True
            # Swap z and x at qubit
            if zq != xq:
                stabilizer.z.xor_bit(qubit)
                stabilizer.x.xor_bit(qubit)

    def prepend_cx(self, qubits):
        ctrl, targ = qubits
        for stabilizer in self.stabs:
            if stabilizer.z.get(ctrl) and stabilizer.x.get(targ):
                stabilizer.sign ^= True
            if stabilizer.z.get(targ):
                stabilizer.z.xor_bit(ctrl)
            if stabilizer.x.get(ctrl):
                stabilizer.x.xor_bit(targ)

    def to_circ(self, inverse=False):
        tab = RowMajorTableau(self.n_qubits)
        for i, stabilizer in enumerate(self.stabs):
            tab.insert_pauli_product(
                PauliProduct(copy.deepcopy(stabilizer.z), copy.deepcopy(stabilizer.x), stabilizer.sign),
                i
            )
        return tab.to_circ(inverse)

class PhasePolynomial:
    def __init__(self, n_qubits):
        self.n_qubits = n_qubits
        self.table = []

    def clifford_correction(self, table, n_qubits):
        tab = RowMajorTableau(n_qubits)
        for i in range(n_qubits):
            for j in range(i + 1, n_qubits):
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
        qc.request_qubits(self.n_qubits)
        for z in self.table:
            pivot = z.get_first_one()
            indices = z.get_all_ones(self.n_qubits)
            if pivot in indices:
                indices.remove(pivot)
            for j in indices:
                qc.add_cnot(j, pivot)
            qc.add_t(pivot)
            for j in reversed(indices):
                qc.add_cnot(j, pivot)
        return qc

def to_remove_indices(table: list[BitVector]) -> list[int]:
    seen = {}
    to_remove = []
    for i, bv in enumerate(table):
        vec = tuple(bv.get_integer_vec())
        first_one = bv.get_first_one()
        if not bv.get(first_one):
            to_remove.append(i)
        elif vec in seen:
            to_remove.append(seen[vec])
            to_remove.append(i)
            del seen[vec]
        else:
            seen[vec] = i
    return to_remove

def to_remove(table: list[BitVector]) -> list[int]:
    seen = {}
    to_remove = []

    for i, vec in enumerate(table):
        vec_int = vec.get_integer_vec()
        first_one = vec.get_first_one()

        if not vec.get(first_one):
            to_remove.append(i)
        elif tuple(vec_int) in seen:
            to_remove.append(seen[tuple(vec_int)])
            to_remove.append(i)
            del seen[tuple(vec_int)]
        else:
            seen[tuple(vec_int)] = i

    return to_remove

def proper(table: list[BitVector]) -> list[BitVector]:
    seen: dict[tuple[bool, ...], int] = {}
    to_remove: list[int] = []
    for i, bv in enumerate(table):
        col: tuple[bool, ...] = tuple(bv.get_boolean_vec())
        first_one: int = bv.get_first_one()
        if not bv.get(first_one):
            to_remove.append(i)
        elif col in seen:
            to_remove.append(seen[col])
            to_remove.append(i)
            del seen[col]
        else:
            seen[col] = i
    to_remove = sorted(set(to_remove), reverse=True)
    for i in to_remove:
        table.pop(i)
    return table

def kernel(matrix: list[BitVector], augmented_matrix: list[BitVector], pivots: dict[int, int]) -> BitVector | None:
    for row_idx, row in enumerate(matrix):
        if row_idx in pivots:
            continue
        # Eliminate current row using existing pivots
        for pivot_row, pivot_col in pivots.items():
            if row.get(pivot_col):
                matrix[row_idx].xor(matrix[pivot_row])
                augmented_matrix[row_idx].xor(augmented_matrix[pivot_row])
        index = row.get_first_one()
        if row.get(index):
            # Eliminate this variable from all pivot rows
            for pivot_row, _ in pivots.items():
                if matrix[pivot_row].get(index):
                    matrix[pivot_row].xor(row)
                    augmented_matrix[pivot_row].xor(augmented_matrix[row_idx])
            pivots[row_idx] = index
        else:
            return copy.deepcopy(augmented_matrix[row_idx])
    return None
