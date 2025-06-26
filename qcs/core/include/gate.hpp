// ─── gate.hpp ────────────────────────────────────────────────────────────────
#pragma once
#include <cstdint>
#include <type_traits>

namespace core {

// ── 1.  gate kinds ────────────────────────────────────────────────────────
enum class GateType : std::uint8_t {
    X        = 0x01,
    Z        = 0x02,
    H        = 0x03,
    CNOT     = 0x04,
    T        = 0x05,
    Td       = 0x06,
    S        = 0x07,
    Sd       = 0x08,
    Toffoli  = 0x09,
    Swap     = 0x0A,
    CZ       = 0x0B,
};

// ── 2.  bit-layout constants  (LSB-oriented) ───────────────────────────────
constexpr std::uint8_t TYPE_BITS = 4;
constexpr std::uint8_t FLAG_BITS = 12;
constexpr std::uint8_t NEG_BITS  = 1;
constexpr std::uint8_t Q_BITS    = 15;

constexpr std::uint8_t TYPE_OFF = 0;
constexpr std::uint8_t FLAG_OFF = TYPE_OFF + TYPE_BITS;
constexpr std::uint8_t N1_OFF   = FLAG_OFF + FLAG_BITS;
constexpr std::uint8_t Q1_OFF   = N1_OFF + NEG_BITS;
constexpr std::uint8_t N2_OFF   = Q1_OFF + Q_BITS;
constexpr std::uint8_t Q2_OFF   = N2_OFF + NEG_BITS;
constexpr std::uint8_t N3_OFF   = Q2_OFF + Q_BITS;
constexpr std::uint8_t Q3_OFF   = N3_OFF + NEG_BITS;

// ── 3.  tiny helper for masks ──────────────────────────────────────────────
constexpr std::uint64_t mask(std::uint8_t bits) {
    return (bits == 64) ? ~0ULL : ((1ULL << bits) - 1ULL);
}

// ── 4.  lightweight wrapper object (8 bytes total) ─────────────────────────
class Gate {
public:
    /* default-construct to zero */
    constexpr Gate() = default;

    /* pack everything in one go (any omitted qubit defaults to “unused”) */
    constexpr Gate(GateType     t,
                   std::uint16_t q1, bool n1 = false,
                   std::uint16_t q2 = 0, bool n2 = false,
                   std::uint16_t q3 = 0, bool n3 = false,
                   std::uint16_t flag = 0)
    { pack(t, q1, n1, q2, n2, q3, n3, flag); }

    // raw 64-bit view  (good for I/O or hashing)
    [[nodiscard]] constexpr std::uint64_t raw() const          { return bits_; }
    constexpr void                         raw(std::uint64_t v){ bits_ = v;    }

    // ------ strongly-typed getters ------------------------------------
    [[nodiscard]] constexpr GateType     type()   const { return GateType(bits(TYPE_OFF, TYPE_BITS)); }
    [[nodiscard]] constexpr std::uint16_t flag()  const { return bits(FLAG_OFF, FLAG_BITS); }

    [[nodiscard]] constexpr bool          neg1()  const { return bits(N1_OFF, NEG_BITS); }
    [[nodiscard]] constexpr std::uint16_t qubit1()const { return bits(Q1_OFF, Q_BITS);   }

    [[nodiscard]] constexpr bool          neg2()  const { return bits(N2_OFF, NEG_BITS); }
    [[nodiscard]] constexpr std::uint16_t qubit2()const { return bits(Q2_OFF, Q_BITS);   }

    [[nodiscard]] constexpr bool          neg3()  const { return bits(N3_OFF, NEG_BITS); }
    [[nodiscard]] constexpr std::uint16_t qubit3()const { return bits(Q3_OFF, Q_BITS);   }

private:
    std::uint64_t bits_ = 0;          // the only data member (8 bytes)

    /* generic slice helpers */
    [[nodiscard]] constexpr std::uint64_t bits(std::uint8_t off,
                                               std::uint8_t len) const
    { return (bits_ >> off) & mask(len); }

    constexpr void set_bits(std::uint8_t off,
                            std::uint8_t len,
                            std::uint64_t v)
    {
        bits_ &= ~(mask(len) << off);          // clear target slice
        bits_ |=  (v & mask(len)) << off;      // store new value
    }

    /* pack routine used by the constructor */
    constexpr void pack(GateType     t,
                        std::uint16_t q1, bool n1,
                        std::uint16_t q2, bool n2,
                        std::uint16_t q3, bool n3,
                        std::uint16_t flag)
    {
        set_bits(TYPE_OFF, TYPE_BITS, static_cast<std::uint64_t>(t));
        set_bits(FLAG_OFF, FLAG_BITS, flag);
        set_bits(N1_OFF,   NEG_BITS,  n1);
        set_bits(Q1_OFF,   Q_BITS,    q1);
        set_bits(N2_OFF,   NEG_BITS,  n2);
        set_bits(Q2_OFF,   Q_BITS,    q2);
        set_bits(N3_OFF,   NEG_BITS,  n3);
        set_bits(Q3_OFF,   Q_BITS,    q3);
    }
};

// compile-time guarantee: still exactly 8 bytes
static_assert(sizeof(Gate) == 8, "Gate must stay 64-bit packed");

} // namespace core
