#include "bitvector.hpp"
#include <sstream>

namespace core {

/* ---------- helpers ---------- */
std::uint64_t BitVector::mask_up_to(std::size_t bits) {
    return bits >= WORD_BITS ? ~0ULL : ((1ULL << bits) - 1ULL);
}

void BitVector::trim_last_word() {
    if (words_.empty()) return;
    std::size_t valid = bit_len_ & (WORD_BITS - 1);
    if (valid) words_.back() &= mask_up_to(valid);
}

/* ---------- ctor / factories ---------- */
BitVector::BitVector(std::size_t size) : bit_len_(size) {
    words_.assign(word_count(), 0ULL);
}

BitVector BitVector::from_integer_vec(const std::vector<int>& vec) {
    BitVector bv(vec.size());
    for (std::size_t i = 0; i < vec.size(); ++i)
        if (vec[i]) bv.xor_bit(i);
    return bv;
}

BitVector BitVector::from_integer(uint64_t v, std::size_t bit_len) {
    BitVector bv(bit_len);  // 64 bits
    for (std::size_t i = 0; i < bit_len; ++i)
        if ((v >> i) & 1ULL) bv.xor_bit(i);
    return bv;
}

// TODO: change this to a hash function
uint64_t BitVector::to_integer() const {
    uint64_t res = 0;
    for (std::size_t i = 0; i < bit_len_; ++i) {
        if (get(i)) res |= (1ULL << i);
    }
    return res;
}

/* ---------- single-bit access ---------- */
bool BitVector::get(std::size_t idx) const {
    if (idx >= bit_len_) return false;
    return (words_[idx >> 6] >> (idx & 63U)) & 1ULL;
}

void BitVector::xor_bit(std::size_t idx) {
    if (idx >= bit_len_) return;
    words_[idx >> 6] ^= 1ULL << (idx & 63U);
}

/* ---------- bulk bitwise ops ---------- */
void BitVector::xor_with(const BitVector& other) {
    std::size_t n = std::min(word_count(), other.word_count());
    for (std::size_t i = 0; i < n; ++i) words_[i] ^= other.words_[i];
    trim_last_word();
}

void BitVector::and_with(const BitVector& other) {
    std::size_t n = std::min(word_count(), other.word_count());
    for (std::size_t i = 0; i < n; ++i) words_[i] &= other.words_[i];
    std::fill(words_.begin() + n, words_.end(), 0ULL);  // extra words become 0
    trim_last_word();
}

void BitVector::swap_with(BitVector& other) {
    std::swap(words_, other.words_);
    std::swap(bit_len_, other.bit_len_);
    trim_last_word();  // clear padding bits in the new last word
    other.trim_last_word();
}

void BitVector::negate() {
    for (auto& w : words_) w = ~w;
    trim_last_word();
}

/* ---------- conversions ---------- */
std::vector<bool> BitVector::get_boolean_vec() const {
    std::vector<bool> v(bit_len_, false);
    for (std::size_t i = 0; i < bit_len_; ++i) v[i] = get(i);
    return v;
}

std::vector<int> BitVector::get_integer_vec() const {
    std::vector<int> v(bit_len_, 0);
    for (std::size_t i = 0; i < bit_len_; ++i) v[i] = get(i) ? 1 : 0;
    return v;
}

std::string BitVector::to_string() const {
    std::string s;
    s.resize(bit_len_);
    for (std::size_t i = 0; i < bit_len_; ++i) s[i] = get(i) ? '1' : '0';
    return s;
}

/* ---------- extras ---------- */


void BitVector::erase_bit(std::size_t idx)
{
    if (idx >= bit_len_)        // out-of-range → no-op
        return;

    const std::size_t old_words = word_count();     // before shrinking
    const std::size_t w_idx     = idx >> 6;         // word that holds the bit
    const std::size_t b_idx     = idx & 63;         // bit offset inside that word

    /* Remove the bit inside its own word.  */
    std::uint64_t low_mask  = (b_idx == 0) ? 0ULL : ((1ULL << b_idx) - 1ULL);
    std::uint64_t word      = words_[w_idx];
    std::uint64_t upper     = (b_idx == 63) ? 0ULL : (word >> (b_idx + 1));

    words_[w_idx] = (word & low_mask) | (upper << b_idx);

    /* Propagate the one-bit left shift across following words.  */
    for (std::size_t w = w_idx + 1; w < old_words; ++w) {
        std::uint64_t cur   = words_[w];
        std::uint64_t carry = cur & 1ULL;            // LSB that wraps
        words_[w - 1] |= carry << 63;               // move it to MSB of prev word
        words_[w]      = cur >> 1;                  // shift current word right by 1
    }

    /* Update length and storage.  */
    --bit_len_;

    // If the last 64-bit word is now completely out of range, drop it.
    if (bit_len_ % WORD_BITS == 0 && !words_.empty())
        words_.pop_back();

    trim_last_word();   // clear padding bits in the new last word
}

void BitVector::extend_vec(const std::vector<bool>& vec) {
    for (bool b : vec) {
        if ((bit_len_ & 63U) == 0) words_.push_back(0ULL);
        if (b) words_.back() |= 1ULL << (bit_len_ & 63U);
        ++bit_len_;
    }
}

std::size_t BitVector::popcount() const {
    std::size_t total = 0;
    for (std::uint64_t w : words_) total += __builtin_popcountll(w);
    return total;
}

std::size_t BitVector::get_first_one() const {
    for (std::size_t word = 0; word < words_.size(); ++word) {
        if (words_[word]) {
            return (word << 6) + __builtin_ctzll(words_[word]);
        }
    }
    return 0;  // same default as Python version
}

std::vector<std::size_t> BitVector::get_all_ones(std::size_t nb_bits) const {
    nb_bits = std::min(nb_bits, bit_len_);
    std::vector<std::size_t> res;
    for (std::size_t i = 0; i < nb_bits; ++i)
        if (get(i)) res.push_back(i);
    return res;
}

} // namespace core
