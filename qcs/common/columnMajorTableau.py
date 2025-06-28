import copy

from .quantumCircuit import QuantumCircuit
from .pauliProduct import PauliProduct
from .bitVector import BitVector
from .rowMajorTableau import RowMajorTableau

class ColumnMajorTableau:
    def __init__(self, n_qubits):
        self.n_qubits = n_qubits
        self.stabs = []
        for i in range(n_qubits):
            z = BitVector(n_qubits)
            z.xor_bit(i)
            x = BitVector(n_qubits)
            self.stabs.append(PauliProduct(z, x, False))

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

    def to_circ(self, inverse=False) -> QuantumCircuit:
        tab = RowMajorTableau(self.n_qubits)
        for i, stabilizer in enumerate(self.stabs):
            tab.insert_pauli_product(
                PauliProduct(copy.deepcopy(stabilizer.z), copy.deepcopy(stabilizer.x), stabilizer.sign),
                i
            )
        return tab.to_circ(inverse)