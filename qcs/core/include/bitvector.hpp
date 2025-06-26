#pragma once
#include <vector>
#include <cstdint>
#include <string>
#include <algorithm>

namespace core {

class BitVector {
public:
    explicit BitVector(std::size_t size = 0);                 // all-zero
    static BitVector from_integer_vec(const std::vector<int>& vec);

    /* ---- size / access ---- */
    std::size_t size() const { return bit_len_; }
    bool        get(std::size_t idx) const;                   // bounds-safe (returns false if idx≥size)

    /* ---- single-bit ops ---- */
    void xor_bit(std::size_t idx);                            // toggle bit if idx valid

    /* ---- bulk ops (up to min(len,other.len)) ---- */
    void xor_with(const BitVector& other);
    void and_with(const BitVector& other);
    void negate();                                            // bitwise NOT (only defined bits)

    /* ---- conversions ---- */
    std::vector<bool> get_boolean_vec()  const;
    std::vector<int>  get_integer_vec()  const;
    std::string       to_string()        const;

    /* ---- extras ---- */
    void              extend_vec(const std::vector<bool>& vec);   // append bits
    std::size_t       popcount()          const;                  // # of 1s
    std::size_t       get_first_one()     const;                  // 1st set bit or 0 if none
    std::vector<std::size_t> get_all_ones(std::size_t nb_bits) const;

private:
    /* storage */
    std::vector<std::uint64_t> words_;   // packed little-endian words
    std::size_t                bit_len_ = 0;

    /* helpers */
    static constexpr std::size_t WORD_BITS = 64;
    std::size_t word_count() const { return (bit_len_ + WORD_BITS - 1) >> 6; }
    static std::uint64_t mask_up_to(std::size_t bits);            // low “bits” ones
    void trim_last_word();                                        // clear padding bits
};

} // namespace core
