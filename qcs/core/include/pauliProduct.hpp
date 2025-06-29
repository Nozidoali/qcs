#pragma once
#include "bitvector.hpp"
#include <vector>

namespace core {

/**
 * PauliProduct represents (z|x, sign) where
 *  – z, x  are BitVectors of length ≥ n_qubits
 *  – sign is the global phase (False → +1, True → –1)
 */
class PauliProduct {
public:
    BitVector z;   ///< Z mask
    BitVector x;   ///< X mask
    bool      sign = false;

    PauliProduct() = default;  // all-zero, no sign
    PauliProduct(BitVector zz, BitVector xx, bool sg = false)
        : z(std::move(zz)), x(std::move(xx)), sign(sg) {}

    /* ---- algebra ---- */
    bool is_commuting   (const PauliProduct& other) const;  // True  ⇔  {self,other}=0
    void pauli_product_mult(const PauliProduct& other);     // in-place  self  ←  self·other

    /* ---- helpers ---- */
    std::vector<bool> get_boolean_vec(std::size_t n_qubits) const;
};

} // namespace core
