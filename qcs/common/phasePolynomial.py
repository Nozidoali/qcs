from .quantumCircuit import QuantumCircuit
from .rowMajorTableau import RowMajorTableau

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