# Reference: https://github.com/VivienVandaele/quantum-circuit-optimization/tree/main 

import copy

class BitVector:
    def __init__(self, size=0):
        self.bits = [False] * size

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

    def clone(self):
        cloned = BitVector(len(self.bits))
        cloned.bits = self.bits[:]
        return cloned

    def __repr__(self):
        return ''.join(['1' if b else '0' for b in self.bits])


class PauliProduct:
    def __init__(self, z, x, sign=False):
        self.z = z  # BitVector
        self.x = x  # BitVector
        self.sign = sign  # bool

    def clone(self):
        return PauliProduct(self.z.clone(), self.x.clone(), self.sign)

    def is_commuting(self, other):
        x1z2 = self.z.clone()
        x1z2.and_(other.x)
        ac = self.x.clone()
        ac.and_(other.z)
        ac.xor(x1z2)
        return ac.popcount() % 2 == 0

    def get_boolean_vec(self, nb_qubits):
        vec_z = self.z.get_boolean_vec()[:nb_qubits]
        vec_x = self.x.get_boolean_vec()[:nb_qubits]
        return vec_z + vec_x

    def pauli_product_mult(self, other):
        x1z2 = self.z.clone()
        x1z2.and_(other.x)
        ac = self.x.clone()
        ac.and_(other.z)
        ac.xor(x1z2)

        self.x.xor(other.x)
        self.z.xor(other.z)

        x1z2 = self.z.clone()
        x1z2.xor(self.x)
        x1z2.xor(other.z)
        x1z2.and_(ac)

        self.sign ^= other.sign ^ (((ac.popcount() + 2 * x1z2.popcount()) % 4) > 1)


class Circuit:
    def __init__(self, nb_qubits):
        self.nb_qubits = nb_qubits
        self.circ = []
        self.ancillas = {}

    def append(self, circ):
        self.circ.extend(circ)

    def decompose_tof(self):
        c = Circuit(self.nb_qubits)
        for gate, qubits in self.circ:
            if (gate == "ccz" or gate == "tof") and len(qubits) == 3:
                if gate == "tof":
                    c.circ.append(("h", [qubits[2]]))
                for i in range(3):
                    c.circ.append(("t", [qubits[i]]))
                c.circ.append(("cx", [qubits[1], qubits[0]]))
                c.circ.append(("x", [qubits[0]]))
                c.circ.append(("t", [qubits[0]]))
                c.circ.append(("x", [qubits[0]]))
                c.circ.append(("cx", [qubits[2], qubits[0]]))
                c.circ.append(("t", [qubits[0]]))
                c.circ.append(("cx", [qubits[1], qubits[0]]))
                c.circ.append(("x", [qubits[0]]))
                c.circ.append(("t", [qubits[0]]))
                c.circ.append(("x", [qubits[0]]))
                c.circ.append(("cx", [qubits[2], qubits[0]]))
                c.circ.append(("cx", [qubits[2], qubits[1]]))
                c.circ.append(("x", [qubits[1]]))
                c.circ.append(("t", [qubits[1]]))
                c.circ.append(("x", [qubits[1]]))
                c.circ.append(("cx", [qubits[2], qubits[1]]))
                if gate == "tof":
                    c.circ.append(("h", [qubits[2]]))
            else:
                c.circ.append((gate, qubits[:]))
        return c

    def get_statistics(self):
        h_count = 0
        internal_h_count = 0
        t_count = 0
        flag = False
        for gate, _ in self.circ:
            if gate == "h":
                h_count += 1
                if flag:
                    internal_h_count += 1
            if gate == "t":
                t_count += 1
                flag = True
        if flag:
            for gate, _ in reversed(self.circ):
                if gate == "h":
                    internal_h_count -= 1
                if gate == "t":
                    break
        return h_count, internal_h_count, t_count

    def hadamard_gadgetization(self):
        c = Circuit(self.nb_qubits)
        anc = Circuit(self.nb_qubits)
        flag = False
        last = 0
        parent_ancilla = list(range(self.nb_qubits))
        for i, (gate, _) in enumerate(self.circ):
            if gate == "t":
                last = i
        for i, (gate, qubits) in enumerate(self.circ):
            if gate == "t":
                flag = True
            if gate == "h" and i < last and flag:
                anc.circ.append(("h", [anc.nb_qubits]))
                c.circ.append(("s", [anc.nb_qubits]))
                c.circ.append(("s", qubits[:]))
                c.circ.append(("cx", [qubits[0], anc.nb_qubits]))
                c.circ.append(("s", [anc.nb_qubits]))
                c.circ.append(("z", [anc.nb_qubits]))
                c.circ.append(("cx", [anc.nb_qubits, qubits[0]]))
                c.circ.append(("cx", [qubits[0], anc.nb_qubits]))
                anc.ancillas[anc.nb_qubits] = parent_ancilla[qubits[0]]
                parent_ancilla[qubits[0]] = anc.nb_qubits
                anc.nb_qubits += 1
            else:
                c.circ.append((gate, qubits[:]))
        c_out = Circuit(anc.nb_qubits)
        c_out.ancillas = anc.ancillas.copy()
        c_out.append(anc.circ[:])
        c_out.append(c.circ[:])
        c_out.append(anc.circ[:])
        return c_out

class SlicedCircuit:
    def __init__(self, nb_qubits):
        self.nb_qubits = nb_qubits
        self.init_circuit = Circuit(nb_qubits)
        self.tableau_vec = []
        self.phase_polynomials = []

    @staticmethod
    def from_circ(circ):
        sliced = SlicedCircuit(circ.nb_qubits)
        sliced.init_circuit.ancillas = circ.ancillas.copy()

        # split initial Clifford and rest
        first_t = next((i for i, (g, _) in enumerate(circ.circ) if g == "t"), len(circ.circ))
        for i in range(first_t):
            gate, q = circ.circ[i]
            sliced.init_circuit.circ.append((gate, q[:]))

        tab = TableauColumnMajor(circ.nb_qubits)
        p = PhasePolynomial(circ.nb_qubits)

        for i, (gate, q) in enumerate(circ.circ):
            if i < first_t:
                continue
            if gate == "h":
                if len(p.table) > 0:
                    sliced.phase_polynomials.append(p)
                    p = PhasePolynomial(circ.nb_qubits)
                tab.prepend_h(q[0])
            elif gate == "x":
                tab.prepend_x(q[0])
            elif gate == "z":
                tab.prepend_z(q[0])
            elif gate == "s":
                tab.prepend_s(q[0])
                tab.prepend_z(q[0])
            elif gate == "cx":
                tab.prepend_cx(q[:])
            elif gate == "t":
                if len(p.table) == 0 and len(sliced.phase_polynomials) > 0:
                    sliced.tableau_vec.append(tab)
                    tab = TableauColumnMajor(circ.nb_qubits)
                p.table.append(tab.stabs[q[0]].z.clone())
                if tab.stabs[q[0]].sign:
                    tab.prepend_s(q[0])
                    tab.prepend_z(q[0])
            else:
                print(f"Operator not implemented: {gate}")
                raise SystemExit(1)

        if len(p.table) > 0:
            sliced.phase_polynomials.append(p)
        sliced.tableau_vec.append(tab)
        return sliced

    def t_opt(self, optimizer: str):
        c = self.init_circuit.clone()
        for i in range(len(self.phase_polynomials)):
            table = self.phase_polynomials[i].table[:]
            if optimizer == "FastTODD":
                self.phase_polynomials[i].table = fast_todd(table[:], self.nb_qubits)
            elif optimizer == "TOHPE":
                self.phase_polynomials[i].table = tohpe(table[:], self.nb_qubits)
            else:
                print(f"Optimizer not implemented: {optimizer}")
                raise SystemExit(1)
            c.append(self.phase_polynomials[i].clifford_correction(table, self.nb_qubits).to_circ(False).circ)
            c.append(self.phase_polynomials[i].to_circ().circ)
            if i < len(self.tableau_vec):
                c.append(self.tableau_vec[i].to_circ(True).circ)
        return c


class Tableau:
    def __init__(self, nb_qubits):
        self.nb_qubits = nb_qubits
        self.z = self.init_z(nb_qubits)
        self.x = self.init_x(nb_qubits)
        self.signs = BitVector(nb_qubits << 1)

    @staticmethod
    def init_z(nb_qubits):
        return [Tableau.unit_vector(i, nb_qubits << 1) for i in range(nb_qubits)]

    @staticmethod
    def init_x(nb_qubits):
        return [Tableau.unit_vector(i + nb_qubits, nb_qubits << 1) for i in range(nb_qubits)]

    @staticmethod
    def unit_vector(pos, size):
        bv = BitVector(size)
        bv.xor_bit(pos)
        return bv

    def append_x(self, qubit):
        self.signs.xor(self.z[qubit])

    def append_z(self, qubit):
        self.signs.xor(self.x[qubit])

    def append_v(self, qubit):
        a = self.x[qubit].clone()
        a.negate()
        a.and_(self.z[qubit])
        self.signs.xor(a)
        self.x[qubit].xor(self.z[qubit])

    def append_s(self, qubit):
        a = self.z[qubit].clone()
        a.and_(self.x[qubit])
        self.signs.xor(a)
        self.z[qubit].xor(self.x[qubit])

    def append_h(self, qubit):
        self.append_s(qubit)
        self.append_v(qubit)
        self.append_s(qubit)

    def append_cx(self, qubits):
        a = self.z[qubits[0]].clone()
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
            if self.z[i].get(col):
                z.xor_bit(i)
            if self.x[i].get(col):
                x.xor_bit(i)
        return PauliProduct(z, x, self.signs.get(col))

    def insert_pauli_product(self, p, col):
        p_x = p.x.get_boolean_vec()
        p_z = p.z.get_boolean_vec()
        for i in range(self.nb_qubits):
            if p_z[i] != self.z[i].get(col):
                self.z[i].xor_bit(col)
            if p_x[i] != self.x[i].get(col):
                self.x[i].xor_bit(col)
        if p.sign != self.signs.get(col):
            self.signs.xor_bit(col)

    def prepend_x(self, qubit):
        self.signs.xor_bit(qubit)

    def prepend_z(self, qubit):
        self.signs.xor_bit(qubit + self.nb_qubits)

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

    def to_circ(self, inverse):
        tab = copy.deepcopy(self)
        c = Circuit(self.nb_qubits)
        for i in range(self.nb_qubits):
            if any(x.get(i) for x in tab.x):
                index = next(j for j, x in enumerate(tab.x) if x.get(i))
                for j in range(i + 1, self.nb_qubits):
                    if tab.x[j].get(i) and j != index:
                        tab.append_cx([index, j])
                        c.circ.append(("cx", [index, j]))
                if tab.z[index].get(i):
                    tab.append_s(index)
                    c.circ.append(("s", [index]))
                tab.append_h(index)
                c.circ.append(("h", [index]))
            if not tab.z[i].get(i):
                index = next(j for j, z in enumerate(tab.z) if z.get(i))
                tab.append_cx([i, index])
                c.circ.append(("cx", [i, index]))
            for j in range(self.nb_qubits):
                if tab.z[j].get(i) and j != i:
                    tab.append_cx([j, i])
                    c.circ.append(("cx", [j, i]))
            for j in range(self.nb_qubits):
                if tab.x[j].get(i + self.nb_qubits) and j != i:
                    tab.append_cx([i, j])
                    c.circ.append(("cx", [i, j]))
            for j in range(self.nb_qubits):
                if tab.z[j].get(i + self.nb_qubits) and j != i:
                    tab.append_cx([i, j])
                    c.circ.append(("cx", [i, j]))
                    tab.append_s(j)
                    c.circ.append(("s", [j]))
                    tab.append_cx([i, j])
                    c.circ.append(("cx", [i, j]))
            if tab.z[i].get(i + self.nb_qubits):
                tab.append_s(i)
                c.circ.append(("s", [i]))
            if tab.signs.get(i):
                tab.append_x(i)
                c.circ.append(("x", [i]))
            if tab.signs.get(i + self.nb_qubits):
                tab.append_z(i)
                c.circ.append(("z", [i]))
        if not inverse:
            c2 = Circuit(self.nb_qubits)
            for gate, qubits in reversed(c.circ):
                c2.circ.append((gate, qubits[:]))
                if gate == "s":
                    c2.circ.append(("z", qubits[:]))
            return c2
        return c

class TableauStab:
    def __init__(self, z: BitVector, x: BitVector, sign: bool = False):
        self.z = z
        self.x = x
        self.sign = sign

    def clone(self):
        return TableauStab(self.z.clone(), self.x.clone(), self.sign)


class TableauColumnMajor:
    def __init__(self, nb_qubits):
        self.nb_qubits = nb_qubits
        self.stabs = []
        for i in range(nb_qubits):
            z = BitVector(nb_qubits)
            x = BitVector(nb_qubits)
            z.xor_bit(i)
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
            zq = stab.z.get(qubit)
            xq = stab.x.get(qubit)
            if zq and xq:
                stab.sign ^= True
            if zq != xq:
                stab.sign ^= False
            # swap z and x
            z_bit = stab.z.get(qubit)
            x_bit = stab.x.get(qubit)
            if z_bit != x_bit:
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
        for i in range(self.nb_qubits):
            tab.insert_pauli_product(
                PauliProduct(self.stabs[i].z.clone(), self.stabs[i].x.clone(), self.stabs[i].sign),
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
        c = Circuit(self.nb_qubits)
        for z in self.table:
            cnot_circ = Circuit(self.nb_qubits)
            pivot = z.get_first_one()
            indices = z.get_all_ones(self.nb_qubits)
            indices.remove(pivot)
            for j in indices:
                cnot_circ.circ.append(("cx", [j, pivot]))
            c.append(cnot_circ.circ[:])
            c.circ.append(("t", [pivot]))
            c.append(cnot_circ.circ)
        return c
def implement_pauli_z_rotation_from_pauli_product(tab, p):
    c = Circuit(tab.nb_qubits)
    cnot_circ = Circuit(tab.nb_qubits)
    pivot = p.z.get_first_one()
    indices = [i for i, b in enumerate(p.z.get_boolean_vec()[:tab.nb_qubits]) if b]
    indices.remove(pivot)
    for j in indices:
        cnot_circ.circ.append(("cx", [j, pivot]))
    c.append(cnot_circ.circ[:])
    c.circ.append(("t", [pivot]))
    if p.sign:
        c.circ.append(("s", [pivot]))
        c.circ.append(("z", [pivot]))
    c.append(cnot_circ.circ)
    return c


def implement_pauli_z_rotation(tab, col):
    pivot = next(i for i, z in enumerate(tab.z) if z.get(col))
    c = Circuit(tab.nb_qubits)
    cnot_circ = Circuit(tab.nb_qubits)
    for j in range(tab.nb_qubits):
        if tab.z[j].get(col) and j != pivot:
            cnot_circ.circ.append(("cx", [j, pivot]))
    c.append(cnot_circ.circ[:])
    c.circ.append(("t", [pivot]))
    if tab.signs.get(col):
        c.circ.append(("s", [pivot]))
        c.circ.append(("z", [pivot]))
    c.append(cnot_circ.circ)
    return c


def implement_pauli_rotation(tab, col):
    c = Circuit(tab.nb_qubits)
    if any(x.get(col) for x in tab.x):
        pivot = next(i for i, x in enumerate(tab.x) if x.get(col))
        for j in range(tab.nb_qubits):
            if tab.x[j].get(col) and j != pivot:
                tab.append_cx([pivot, j])
                c.circ.append(("cx", [pivot, j]))
        if tab.z[pivot].get(col):
            tab.append_s(pivot)
            c.circ.append(("s", [pivot]))
        tab.append_h(pivot)
        c.circ.append(("h", [pivot]))
    c.append(implement_pauli_z_rotation(tab, col).circ)
    return c


def implement_tof(tab, cols, h_gate):
    c = Circuit(tab.nb_qubits)
    c.append(implement_pauli_rotation(tab, cols[0]).circ)
    c.append(implement_pauli_rotation(tab, cols[1]).circ)
    c.append(implement_pauli_rotation(tab, cols[2] + tab.nb_qubits * int(h_gate)).circ)

    p0 = tab.extract_pauli_product(cols[0])
    p1 = tab.extract_pauli_product(cols[1])
    p2 = tab.extract_pauli_product(cols[2] + tab.nb_qubits * int(h_gate))

    p0.z.xor(p1.z)
    p0.sign ^= p1.sign ^ True
    c.append(implement_pauli_z_rotation_from_pauli_product(tab, p0).circ)

    p0.z.xor(p2.z)
    p0.sign ^= p2.sign ^ True
    c.append(implement_pauli_z_rotation_from_pauli_product(tab, p0).circ)

    p0.z.xor(p1.z)
    p0.sign ^= p1.sign ^ True
    c.append(implement_pauli_z_rotation_from_pauli_product(tab, p0).circ)

    p1.z.xor(p2.z)
    p1.sign ^= p2.sign ^ True
    c.append(implement_pauli_z_rotation_from_pauli_product(tab, p1).circ)

    return c


def h_opt_reverse(c_in):
    tab = Tableau(c_in.nb_qubits)
    for gate, q in c_in.circ:
        if gate == "h":
            tab.prepend_h(q[0])
        elif gate == "x":
            tab.prepend_x(q[0])
        elif gate == "z":
            tab.prepend_z(q[0])
        elif gate == "s":
            tab.prepend_s(q[0])
            tab.prepend_z(q[0])
        elif gate == "cx":
            tab.prepend_cx(q)
        elif gate in {"t", "tof", "ccz"}:
            continue
        else:
            raise NotImplementedError(f"Operator not implemented: {gate}")

    for gate, q in reversed(c_in.circ):
        if gate == "h":
            tab.prepend_h(q[0])
        elif gate == "x":
            tab.prepend_x(q[0])
        elif gate == "z":
            tab.prepend_z(q[0])
        elif gate == "s":
            tab.prepend_s(q[0])
        elif gate == "cx":
            tab.prepend_cx(q)
        elif gate == "t":
            implement_pauli_rotation(tab, q[0])
        elif gate == "tof":
            implement_tof(tab, q, True)
        elif gate == "ccz":
            implement_tof(tab, q, False)
        else:
            raise NotImplementedError(f"Operator not implemented: {gate}")

    return tab


def internal_h_opt(c_in):
    tab = h_opt_reverse(c_in)
    c = tab.to_circ(inverse=False)
    for gate, q in c_in.circ:
        if gate == "h":
            tab.prepend_h(q[0])
        elif gate == "x":
            tab.prepend_x(q[0])
        elif gate == "z":
            tab.prepend_z(q[0])
        elif gate == "s":
            tab.prepend_s(q[0])
            tab.prepend_z(q[0])
        elif gate == "cx":
            tab.prepend_cx(q)
        elif gate == "t":
            c.append(implement_pauli_rotation(tab, q[0]).circ)
        elif gate == "tof":
            c.append(implement_tof(tab, q, True).circ)
        elif gate == "ccz":
            c.append(implement_tof(tab, q, False).circ)
        else:
            raise NotImplementedError(f"Operator not implemented: {gate}")
    c.append(tab.to_circ(inverse=True).circ)
    return c

def proper(table):
    seen = {}
    to_remove = []
    for i, bv in enumerate(table):
        col = tuple(bv.get_boolean_vec())
        first_one = bv.get_first_one()
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


def kernel(matrix, augmented_matrix, pivots):
    for i in range(len(matrix)):
        if i in pivots:
            continue
        for j in list(pivots):
            if matrix[i].get(pivots[j]):
                matrix[i].xor(matrix[j])
                augmented_matrix[i].xor(augmented_matrix[j])
        index = matrix[i].get_first_one()
        if matrix[i].get(index):
            for j in pivots:
                if matrix[j].get(index):
                    matrix[j].xor(matrix[i])
                    augmented_matrix[j].xor(augmented_matrix[i])
            pivots[i] = index
        else:
            return augmented_matrix[i].clone()
    return None

def diagonalize_pauli_rotation(tab, col):
    if any(x.get(col) for x in tab.x):
        pivot = next(i for i, x in enumerate(tab.x) if x.get(col))
        for j in range(tab.nb_qubits):
            if tab.x[j].get(col) and j != pivot:
                tab.append_cx([pivot, j])
        if tab.z[pivot].get(col):
            tab.append_s(pivot)
        tab.append_h(pivot)
        return True
    return False


def diagonalize_tof(tab, cols, h_gate):
    vec = []
    vec.append(diagonalize_pauli_rotation(tab, cols[0]))
    vec.append(diagonalize_pauli_rotation(tab, cols[1]))
    vec.append(diagonalize_pauli_rotation(tab, cols[2] + tab.nb_qubits * int(h_gate)))
    vec.extend([False] * 4)  # match Rust-style output
    return vec


def reverse_diagonalization(c_in):
    tab = Tableau(c_in.nb_qubits)
    for gate, q in c_in.circ:
        if gate == "h":
            tab.prepend_h(q[0])
        elif gate == "x":
            tab.prepend_x(q[0])
        elif gate == "z":
            tab.prepend_z(q[0])
        elif gate == "s":
            tab.prepend_s(q[0])
            tab.prepend_z(q[0])
        elif gate == "cx":
            tab.prepend_cx(q)
        elif gate in {"t", "tof", "ccz"}:
            continue
        else:
            raise NotImplementedError(f"Operator not implemented: {gate}")

    for gate, q in reversed(c_in.circ):
        if gate == "h":
            tab.prepend_h(q[0])
        elif gate == "x":
            tab.prepend_x(q[0])
        elif gate == "z":
            tab.prepend_z(q[0])
        elif gate == "s":
            tab.prepend_s(q[0])
        elif gate == "cx":
            tab.prepend_cx(q)
        elif gate == "t":
            diagonalize_pauli_rotation(tab, q[0])
        elif gate == "tof":
            diagonalize_tof(tab, q, True)
        elif gate == "ccz":
            diagonalize_tof(tab, q, False)
        else:
            raise NotImplementedError(f"Operator not implemented: {gate}")
    return tab


def rank_vector(c_in):
    tab = reverse_diagonalization(c_in)
    vec = []
    for gate, q in c_in.circ:
        if gate == "h":
            tab.prepend_h(q[0])
        elif gate == "x":
            tab.prepend_x(q[0])
        elif gate == "z":
            tab.prepend_z(q[0])
        elif gate == "s":
            tab.prepend_s(q[0])
            tab.prepend_z(q[0])
        elif gate == "cx":
            tab.prepend_cx(q)
        elif gate == "t":
            vec.append(diagonalize_pauli_rotation(tab, q[0]))
        elif gate == "tof":
            vec.extend(diagonalize_tof(tab, q, True))
        elif gate == "ccz":
            vec.extend(diagonalize_tof(tab, q, False))
        else:
            raise NotImplementedError(f"Operator not implemented: {gate}")
    return vec

def fast_todd(table, nb_qubits):
    table = [bv.clone() for bv in table]

    while True:
        table = tohpe(table, nb_qubits)

        matrix = [bv.clone() for bv in table]
        for i in range(len(matrix)):
            t_vec = matrix[i].get_boolean_vec()[:nb_qubits]
            extended = []
            for _ in range(nb_qubits):
                if t_vec.pop():
                    extended += t_vec.copy()
                else:
                    extended += [False] * len(t_vec)
            matrix[i].extend_vec(extended, nb_qubits)

        pivots = {}
        augmented = []
        for i in range(len(table)):
            bv = BitVector(len(table))
            bv.xor_bit(i)
            augmented.append(bv)

        kernel(matrix, augmented, pivots)
        pivots = {v: k for k, v in pivots.items()}
        row_map = {bv.get_integer_vec(): i for i, bv in enumerate(table)}

        max_score = 0
        max_z, max_y = None, None
        for i in range(len(table)):
            for j in range(i + 1, len(table)):
                z = table[i].clone()
                z.xor(table[j])
                z_vec = z.get_boolean_vec()

                r_mat = []
                r_aug = []
                for k in range(nb_qubits):
                    col = BitVector(len(matrix[0]))
                    a_col = BitVector(len(augmented[0]))
                    idx = 0
                    for a in reversed(range(nb_qubits)):
                        for b in range(a):
                            if (a == k and z_vec[b]) or (b == k and z_vec[a]):
                                col.xor_bit(nb_qubits + idx)
                                if nb_qubits + idx in pivots:
                                    col.xor(matrix[pivots[nb_qubits + idx]])
                                    a_col.xor(augmented[pivots[nb_qubits + idx]])
                            idx += 1
                    r_mat.append(col)
                    r_aug.append(a_col)

                col = BitVector(len(matrix[0]))
                a_col = BitVector(len(augmented[0]))
                idx = 0
                for a in reversed(range(nb_qubits)):
                    for b in range(a):
                        if z_vec[a] and z_vec[b]:
                            col.xor_bit(nb_qubits + idx)
                            if nb_qubits + idx in pivots:
                                col.xor(matrix[pivots[nb_qubits + idx]])
                                a_col.xor(augmented[pivots[nb_qubits + idx]])
                        idx += 1
                    if z_vec[a]:
                        col.xor_bit(a)
                        if a in pivots:
                            col.xor(matrix[pivots[a]])
                            a_col.xor(augmented[pivots[a]])
                r_mat.append(col)
                r_aug.append(a_col)

                for k in range(len(r_mat)):
                    idx = r_mat[k].get_first_one()
                    if r_mat[k].get(idx):
                        pivot = r_mat[k].clone()
                        aug_pivot = r_aug[k].clone()
                        for l in range(k + 1, len(r_mat)):
                            if r_mat[l].get(idx):
                                r_mat[l].xor(pivot)
                                r_aug[l].xor(aug_pivot)
                    elif r_aug[k].get(i) ^ r_aug[k].get(j):
                        score = 0
                        y = r_aug[k].clone()
                        for l in range(len(table)):
                            if y.get(l):
                                table[l].xor(z)
                                if table[l].get_integer_vec() in row_map and not y.get(row_map[table[l].get_integer_vec()]):
                                    score += 2
                                table[l].xor(z)
                        if y.popcount() % 2 == 1:
                            if z.get_integer_vec() in row_map:
                                score += 1
                            else:
                                score -= 1
                        if score > max_score:
                            max_score = score
                            max_y = y
                            max_z = z.clone()

        if max_score == 0:
            break

        y = max_y
        z = max_z
        for i in range(len(table)):
            if y.get(i):
                table[i].xor(z)
        if y.popcount() % 2 == 1:
            table.append(z)
        table = proper(table)

    return table


def tohpe(table, nb_qubits):
    from collections import defaultdict

    def clear_column(i, matrix, augmented_matrix, pivots):
        if i not in pivots:
            return
        val = pivots.pop(i)
        if not augmented_matrix[i].get(i):
            for j in range(len(matrix)):
                if augmented_matrix[j].get(i):
                    pivots[j] = val
                    matrix[j], matrix[i] = matrix[i], matrix[j]
                    augmented_matrix[j], augmented_matrix[i] = augmented_matrix[i], augmented_matrix[j]
                    break
        col = matrix[i].clone()
        aug_col = augmented_matrix[i].clone()
        for j in range(len(matrix)):
            if j != i and augmented_matrix[j].get(i):
                matrix[j].xor(col)
                augmented_matrix[j].xor(aug_col)

    matrix = [bv.clone() for bv in table]
    for i in range(len(table)):
        t_vec = table[i].get_boolean_vec()[:nb_qubits]
        vec = []
        for _ in range(nb_qubits):
            if t_vec.pop():
                vec += t_vec.copy()
            else:
                vec += [False] * len(t_vec)
        matrix[i].extend_vec(vec, nb_qubits)

    pivots = {}
    augmented_matrix = []
    for i in range(len(table)):
        bv = BitVector(len(table))
        bv.xor_bit(i)
        augmented_matrix.append(bv)

    while True:
        y = kernel(matrix, augmented_matrix, pivots)
        if y is None:
            break

        parity = y.popcount() % 2 == 1
        score_map = defaultdict(int)

        for i in range(len(table)):
            cond = y.get(i)
            vec_key = table[i].get_integer_vec()
            if (parity and not cond) or (not parity and cond):
                score_map[tuple(vec_key)] = 1

        for i in range(len(table)):
            if not y.get(i):
                continue
            for j in range(len(table)):
                if y.get(j):
                    continue
                z = table[i].clone()
                z.xor(table[j])
                key = tuple(z.get_integer_vec())
                score_map[key] += 2

        max_key = None
        max_val = 0
        for key, val in score_map.items():
            if val > max_val or (val == max_val and (max_key is None or key < max_key)):
                max_key = key
                max_val = val

        if max_val <= 0:
            break

        z = BitVector.from_integer_vec(list(max_key))
        to_update = y.get_boolean_vec()[:len(table)]
        if y.popcount() % 2 == 1:
            table.append(BitVector(table[0].size()))
            matrix.append(BitVector(matrix[0].size()))
            new_aug = BitVector(len(table))
            new_aug.xor_bit(len(augmented_matrix))
            augmented_matrix.append(new_aug)
            to_update.append(True)

        indices = [i for i, val in enumerate(to_update) if val]
        for i in indices:
            table[i].xor(z)

        to_remove = to_remove_indices(table)
        to_remove.sort(reverse=True)
        for i in to_remove:
            clear_column(i, matrix, augmented_matrix, pivots)
            table.pop(i)
            matrix.pop(i)
            augmented_matrix.pop(i)
            to_update.pop(i)

        size = len(table)
        for i in range(len(augmented_matrix)):
            while augmented_matrix[i].size() > size:
                augmented_matrix[i].blocks.pop()

        for i in indices:
            clear_column(i, matrix, augmented_matrix, pivots)
            matrix[i] = table[i].clone()
            bv = BitVector(len(table))
            bv.xor_bit(i)
            augmented_matrix[i] = bv
            t_vec = table[i].get_boolean_vec()[:nb_qubits]
            vec = []
            for _ in range(nb_qubits):
                if t_vec.pop():
                    vec += t_vec.copy()
                else:
                    vec += [False] * len(t_vec)
            matrix[i].extend_vec(vec, nb_qubits)

    return table


def to_remove_indices(table):
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
