import copy

from .bitVector import BitVector

class PauliProduct:
    def __init__(self, z: BitVector, x: BitVector, sign=False):
        self.z: BitVector = z  # BitVector
        self.x: BitVector = x  # BitVector
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