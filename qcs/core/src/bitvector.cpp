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
