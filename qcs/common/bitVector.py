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