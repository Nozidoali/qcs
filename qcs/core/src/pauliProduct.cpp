#include "pauliProduct.hpp"

namespace core {

/* ------------------------------------------------------------------ *
 *  Commutation check                                                 *
 * ------------------------------------------------------------------ */
bool PauliProduct::is_commuting(const PauliProduct& other) const {
    BitVector tmp1 = z;        // z₁
    tmp1.and_with(other.x);    // z₁ ∧ x₂

    BitVector tmp2 = x;        // x₁
    tmp2.and_with(other.z);    // x₁ ∧ z₂

    tmp1.xor_with(tmp2);       // (z₁·x₂) ⊕ (x₁·z₂)
    return (tmp1.popcount() & 1U) == 0U;  // even → commute
}

/* ------------------------------------------------------------------ *
 *  In-place multiplication  self ← self·other                        *
 *  (phase tracked in `sign`)                                         *
 * ------------------------------------------------------------------ */
void PauliProduct::pauli_product_mult(const PauliProduct& other) {
    /* ac = (z₁·x₂) ⊕ (x₁·z₂)  (bit-vector) */
    BitVector ac = z;
    ac.and_with(other.x);
    {
        BitVector t = x;
        t.and_with(other.z);
        ac.xor_with(t);
    }

    /* self masks get XOR-added */
    x.xor_with(other.x);
    z.xor_with(other.z);

    /* x1z2 = (z ⊕ x ⊕ z₂) ∧ ac   after update of z/x */
    BitVector x1z2 = z;
    x1z2.xor_with(x);
    x1z2.xor_with(other.z);
    x1z2.and_with(ac);

    /* Phase update:
       sign ← sign ⊕ sign₂ ⊕ ((|ac| + 2|x1z2|) mod 4 > 1)
    */
    std::size_t p  = ac.popcount();
    std::size_t q  = x1z2.popcount();
    bool phase_flip = ((p + (q << 1)) & 3U) > 1U;

    sign ^= other.sign ^ phase_flip;
}

/* ------------------------------------------------------------------ *
 *  Boolean vector  [ Z₀…Z_{n-1} | X₀…X_{n-1} ]                       *
 * ------------------------------------------------------------------ */
std::vector<bool> PauliProduct::get_boolean_vec(std::size_t n_qubits) const {
    std::vector<bool> out;
    out.reserve(n_qubits << 1);
    auto zb = z.get_boolean_vec();
    auto xb = x.get_boolean_vec();
    out.insert(out.end(), zb.begin(), zb.begin() + std::min(n_qubits, zb.size()));
    out.insert(out.end(), xb.begin(), xb.begin() + std::min(n_qubits, xb.size()));
    return out;
}

} // namespace core
