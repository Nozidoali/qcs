# Reference: https://github.com/VivienVandaele/quantum-circuit-optimization/tree/main 

import copy

from stabilizerTableau import *
from quantumCircuit import *

def fast_todd(table, nb_qubits):
    """
    FastTODD algorithm for phase polynomial optimization.
    """
    table = [copy.deepcopy(bv) for bv in table]

    while True:
        table = tohpe(table, nb_qubits)

        # Build extended matrix for kernel computation
        matrix = [copy.deepcopy(bv) for bv in table]
        for i in range(len(matrix)):
            t_vec = matrix[i].get_boolean_vec()[:nb_qubits]
            extended = []
            for _ in range(nb_qubits):
                if t_vec and t_vec.pop(0):
                    extended += t_vec.copy()
                else:
                    extended += [False] * len(t_vec)
            matrix[i].extend_vec(extended, len(extended))

        pivots = {}
        augmented = []
        for i in range(len(table)):
            bv = BitVector(len(table))
            bv.xor_bit(i)
            augmented.append(bv)

        kernel(matrix, augmented, pivots)
        pivots = {v: k for k, v in pivots.items()}
        # Use tuple for hashable keys
        row_map = {tuple(bv.get_integer_vec()): i for i, bv in enumerate(table)}

        max_score = 0
        max_z, max_y = None, None
        for i in range(len(table)):
            for j in range(i + 1, len(table)):
                z = copy.deepcopy(table[i])
                z.xor(table[j])
                z_vec = z.get_boolean_vec()

                r_mat, r_aug = [], []
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

                # Last column for quadratic terms
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

                # Row reduction
                for k in range(len(r_mat)):
                    idx = r_mat[k].get_first_one()
                    if r_mat[k].get(idx):
                        pivot = copy.deepcopy(r_mat[k])
                        aug_pivot = copy.deepcopy(r_aug[k])
                        for l in range(k + 1, len(r_mat)):
                            if r_mat[l].get(idx):
                                r_mat[l].xor(pivot)
                                r_aug[l].xor(aug_pivot)
                    elif r_aug[k].get(i) ^ r_aug[k].get(j):
                        score = 0
                        y = copy.deepcopy(r_aug[k])
                        for l in range(len(table)):
                            if y.get(l):
                                table[l].xor(z)
                                key = tuple(table[l].get_integer_vec())
                                if key in row_map and not y.get(row_map[key]):
                                    score += 2
                                table[l].xor(z)
                        if y.popcount() % 2 == 1:
                            key = tuple(z.get_integer_vec())
                            score += 1 if key in row_map else -1
                        if score > max_score:
                            max_score = score
                            max_y = y
                            max_z = copy.deepcopy(z)

        if max_score == 0:
            break

        y, z = max_y, max_z
        for i in range(len(table)):
            if y.get(i):
                table[i].xor(z)
        if y.popcount() % 2 == 1:
            table.append(z)
        table = proper(table)

    return table

def tohpe(table: list['BitVector'], nb_qubits: int) -> list['BitVector']:
    """
    Simplified and commented version of TOHPE algorithm.
    Attempts to reduce the number of phase polynomial terms.
    """
    def clear_column(i: int, matrix: list['BitVector'], augmented: list['BitVector'], pivots: dict[int, int]) -> None:
        # Remove column i from pivots and clear it from matrix and augmented
        if i not in pivots:
            return
        val = pivots.pop(i)
        if not augmented[i].get(i):
            for j in range(len(matrix)):
                if augmented[j].get(i):
                    pivots[j] = val
                    matrix[i], matrix[j] = copy.deepcopy(matrix[j]), copy.deepcopy(matrix[i])
                    augmented[i], augmented[j] = copy.deepcopy(augmented[j]), copy.deepcopy(augmented[i])
                    break
        col, aug_col = copy.deepcopy(matrix[i]), copy.deepcopy(augmented[i])
        for j in range(len(matrix)):
            if j != i and augmented[j].get(i):
                matrix[j].xor(col)
                augmented[j].xor(aug_col)

    # Prepare extended table for kernel computation
    matrix = [copy.deepcopy(bv) for bv in table]
    for i, row in enumerate(table):
        t_vec = row.get_boolean_vec()[:nb_qubits]
        ext = []
        for _ in range(nb_qubits):
            ext += t_vec.copy() if t_vec and t_vec.pop(0) else [False] * len(t_vec)
        matrix[i].extend_vec(ext, nb_qubits)

    pivots: dict[int, int] = {}
    augmented = [BitVector(len(table)) for _ in table]
    for i, e in enumerate(augmented):
        e.xor_bit(i)

    while True:
        
        print(f"[INFO] Current number of rows: {len(matrix)}")
        y = kernel(matrix, augmented, pivots)
        if y is None:
            break

        # Score possible reductions
        score_map = {}
        parity = (y.popcount() & 1) == 1
        for i, row in enumerate(table):
            key = tuple(row.get_integer_vec())
            if (parity and not y.get(i)) or (not parity and y.get(i)):
                score_map[key] = 1

        for i in range(len(table)):
            if not y.get(i):
                continue
            for j in range(len(table)):
                if y.get(j):
                    continue
                z = copy.deepcopy(table[i])
                z.xor(table[j])
                key = tuple(z.get_integer_vec())
                score_map[key] = score_map.get(key, 0) + 2

        # Find best reduction
        best_key = None
        best_val = 0
        for k, v in score_map.items():
            if v > best_val or (v == best_val and (best_key is None or k < best_key)):
                best_key, best_val = k, v
        if best_val <= 0:
            break

        z = BitVector.from_integer_vec(list(best_key))
        to_update = y.get_boolean_vec()[:len(table)]

        # If y has odd parity, append new row to all tables
        if y.popcount() & 1:
            new_len = len(table[0].bits)
            table.append(BitVector(new_len))
            matrix.append(BitVector(len(matrix[0].bits)))
            e = BitVector(len(table))
            e.xor_bit(len(augmented))
            augmented.append(e)
            to_update.append(True)

        # Apply reduction
        affected = [idx for idx, f in enumerate(to_update) if f]
        for idx in affected:
            table[idx].xor(z)

        # Remove duplicate or zero rows, keep tables in sync
        remove_idxs = sorted(to_remove(table), reverse=True)
        for idx in remove_idxs:
            clear_column(idx, matrix, augmented, pivots)
            table.pop(idx)
            matrix.pop(idx)
            augmented.pop(idx)
            to_update.pop(idx)
        # Truncate augmented rows to match table length
        for row in augmented:
            row.bits = row.bits[:len(table)]

        # Update ext_table and augmented for affected rows
        for idx in affected:
            if idx >= len(table):  # skip if row was removed
                continue
            clear_column(idx, matrix, augmented, pivots)
            matrix[idx] = copy.deepcopy(table[idx])
            e = BitVector(len(table))
            e.xor_bit(idx)
            augmented[idx] = e
            t_vec = table[idx].get_boolean_vec()[:nb_qubits]
            ext = []
            for _ in range(nb_qubits):
                ext += t_vec.copy() if t_vec and t_vec.pop(0) else [False] * len(t_vec)
            matrix[idx].extend_vec(ext, nb_qubits)

        # Ensure ext_table and table have the same number of rows
        while len(matrix) < len(table):
            matrix.append(BitVector(len(matrix[0].bits)))
        while len(matrix) > len(table):
            matrix.pop()

    return table

class SlicedCircuit:
    def __init__(self, nb_qubits):
        self.nb_qubits = nb_qubits
        self.init_circuit = QuantumCircuit()
        self.init_circuit.request_qubits(nb_qubits)
        self.tableau_vec = []
        self.phase_polynomials = []

    @staticmethod
    def from_circ(circ: QuantumCircuit) -> "SlicedCircuit":
        sliced = SlicedCircuit(circ.n_qubits)

        first_t = circ.first_t
        for g in circ.gates[:first_t]:
            sliced.init_circuit.add_gate(g)

        tab = TableauColumnMajor(circ.n_qubits)
        poly = PhasePolynomial(circ.n_qubits)

        for idx, gate in enumerate(circ.gates):
            if idx < first_t:
                continue

            name = gate["name"]
            if name == "HAD":
                if poly.table:
                    sliced.phase_polynomials.append(poly)
                    poly = PhasePolynomial(circ.n_qubits)
                tab.prepend_h(gate["target"])

            elif name == "X":
                tab.prepend_x(gate["target"])

            elif name == "Z":
                tab.prepend_z(gate["target"])

            elif name == "S":
                q = gate["target"]
                tab.prepend_s(q)
                tab.prepend_z(q)

            elif name == "CNOT":
                tab.prepend_cx([gate["ctrl"], gate["target"]])

            elif name in ("T", "Tdg"):
                q = gate["target"]
                if not poly.table and sliced.phase_polynomials:
                    sliced.tableau_vec.append(tab)
                    tab = TableauColumnMajor(circ.n_qubits)

                poly.table.append(copy.deepcopy(tab.stabs[q].z))
                if tab.stabs[q].sign:
                    tab.prepend_s(q)
                    tab.prepend_z(q)

            else:
                raise NotImplementedError(f"Unsupported gate {name}")

        if poly.table:
            sliced.phase_polynomials.append(poly)
        sliced.tableau_vec.append(tab)
        return sliced

    def t_opt(self, optimizer: str):
        _circuit = copy.deepcopy(self.init_circuit)
        for i in range(len(self.phase_polynomials)):
            table = self.phase_polynomials[i].table[:]
            if optimizer == "FastTODD":
                self.phase_polynomials[i].table = fast_todd(table[:], self.nb_qubits)
            elif optimizer == "TOHPE":
                self.phase_polynomials[i].table = tohpe(table[:], self.nb_qubits)
            else:
                print(f"Optimizer not implemented: {optimizer}")
                raise SystemExit(1)
            _circuit.append(self.phase_polynomials[i].clifford_correction(table, self.nb_qubits).to_circ(False))
            _circuit.append(self.phase_polynomials[i].to_circ())
            if i < len(self.tableau_vec):
                _circuit.append(self.tableau_vec[i].to_circ(True))
        return _circuit

def implement_pauli_z_rotation_from_pauli_product(tab, p) -> QuantumCircuit:
    qc = QuantumCircuit(); qc.request_qubits(tab.nb_qubits)
    blk = QuantumCircuit(); blk.request_qubits(tab.nb_qubits)
    pivot = p.z.get_first_one()
    for j in [i for i,b in enumerate(p.z.get_boolean_vec()[:tab.nb_qubits]) if b and i != pivot]:
        blk.add_cnot(j, pivot)
    qc.append(blk)
    qc.add_t(pivot)
    if p.sign:
        qc.add_s(pivot); qc.add_z(pivot)
    qc.append(blk)
    return qc

def implement_pauli_z_rotation(tab, col) -> QuantumCircuit:
    pivot = next(i for i,z in enumerate(tab.z) if z.get(col))
    qc = QuantumCircuit(); qc.request_qubits(tab.nb_qubits)
    blk = QuantumCircuit(); blk.request_qubits(tab.nb_qubits)
    for j in range(tab.nb_qubits):
        if tab.z[j].get(col) and j != pivot:
            blk.add_cnot(j, pivot)
    qc.append(blk)
    qc.add_t(pivot)
    if tab.signs.get(col):
        qc.add_s(pivot); qc.add_z(pivot)
    qc.append(blk)
    return qc

def implement_pauli_rotation(tab, col) -> QuantumCircuit:
    qc = QuantumCircuit(); qc.request_qubits(tab.nb_qubits)
    if any(x.get(col) for x in tab.x):
        pivot = next(i for i,x in enumerate(tab.x) if x.get(col))
        for j in range(tab.nb_qubits):
            if tab.x[j].get(col) and j != pivot:
                tab.append_cx([pivot, j]); qc.add_cnot(pivot, j)
        if tab.z[pivot].get(col):
            tab.append_s(pivot); qc.add_s(pivot)
        tab.append_h(pivot); qc.add_h(pivot)
    qc.append(implement_pauli_z_rotation(tab, col))
    return qc

def implement_tof(tab, cols, h_gate: bool) -> QuantumCircuit:
    qc = QuantumCircuit(); qc.request_qubits(tab.nb_qubits)
    qc.append(implement_pauli_rotation(tab, cols[0]))
    qc.append(implement_pauli_rotation(tab, cols[1]))
    qc.append(implement_pauli_rotation(tab, cols[2] + tab.nb_qubits * int(h_gate)))
    p0 = tab.extract_pauli_product(cols[0]); p1 = tab.extract_pauli_product(cols[1])
    p2 = tab.extract_pauli_product(cols[2] + tab.nb_qubits * int(h_gate))
    p0.z.xor(p1.z); p0.sign ^= p1.sign ^ True; qc.append(implement_pauli_z_rotation_from_pauli_product(tab, p0))
    p0.z.xor(p2.z); p0.sign ^= p2.sign ^ True; qc.append(implement_pauli_z_rotation_from_pauli_product(tab, p0))
    p0.z.xor(p1.z); p0.sign ^= p1.sign ^ True; qc.append(implement_pauli_z_rotation_from_pauli_product(tab, p0))
    p1.z.xor(p2.z); p1.sign ^= p2.sign ^ True; qc.append(implement_pauli_z_rotation_from_pauli_product(tab, p1))
    return qc

def h_opt_reverse(c_in: QuantumCircuit) -> Tableau:
    tab = Tableau(c_in.n_qubits)
    for gate in c_in.gates:
        name, q = gate["name"], gate
        if name == "HAD":
            tab.prepend_h(q["target"])
        elif name == "X":
            tab.prepend_x(q["target"])
        elif name == "Z":
            tab.prepend_z(q["target"])
        elif name == "S":
            tab.prepend_s(q["target"]); tab.prepend_z(q["target"])
        elif name == "CNOT":
            tab.prepend_cx([q["ctrl"], q["target"]])
    for gate in reversed(c_in.gates):
        name, q = gate["name"], gate
        if name == "HAD":
            tab.prepend_h(q["target"])
        elif name == "X":
            tab.prepend_x(q["target"])
        elif name == "Z":
            tab.prepend_z(q["target"])
        elif name == "S":
            tab.prepend_s(q["target"])
        elif name == "CNOT":
            tab.prepend_cx([q["ctrl"], q["target"]])
        elif name in {"T", "Tdg"}:
            implement_pauli_rotation(tab, q["target"])
        elif name == "Tof":
            implement_tof(tab, [q["ctrl1"], q["ctrl2"], q["target"]], True)
        elif name == "CCZ":
            implement_tof(tab, [q["ctrl1"], q["ctrl2"], q["target"]], False)
        else:
            raise NotImplementedError(name)
    return tab

def internal_h_opt(c_in: QuantumCircuit) -> QuantumCircuit:
    tab = h_opt_reverse(c_in)
    c = tab.to_circ(inverse=False)
    for gate in c_in.gates:
        name, q = gate["name"], gate
        if name == "HAD":
            tab.prepend_h(q["target"])
        elif name == "X":
            tab.prepend_x(q["target"])
        elif name == "Z":
            tab.prepend_z(q["target"])
        elif name == "S":
            tab.prepend_s(q["target"]); tab.prepend_z(q["target"])
        elif name == "CNOT":
            tab.prepend_cx([q["ctrl"], q["target"]])
        elif name in {"T", "Tdg"}:
            c.append(implement_pauli_rotation(tab, q["target"]))
        elif name == "Tof":
            c.append(implement_tof(tab, [q["ctrl1"], q["ctrl2"], q["target"]], True))
        elif name == "CCZ":
            c.append(implement_tof(tab, [q["ctrl1"], q["ctrl2"], q["target"]], False))
        else:
            raise NotImplementedError(name)
    c.append(tab.to_circ(inverse=True))
    return c

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

def t_count_optimization(circuit: QuantumCircuit, method: str = "FastTODD") -> QuantumCircuit:
    circuit = circuit.to_basic_gates()
    print(f"[INFO] number of internal H gates before optimization: {circuit.num_internal_h}")
    circuit = internal_h_opt(circuit)
    print(f"[INFO] number of internal H gates before gadgetization: {circuit.num_internal_h}")
    circuit = circuit.hadamard_gadgetization()
    print(f"[INFO] number of internal H gates after gadgetization: {circuit.num_internal_h}")
    sliced_circuit = SlicedCircuit.from_circ(circuit)
    optimized_circuit = sliced_circuit.t_opt(method)
    return optimized_circuit

