#include "gate.hpp"

namespace core {

bool is_t(const Gate& gate) {
    return gate.type() == GateType::T || gate.type() == GateType::Td;
}

Gate map_qubits(const Gate& gate, const std::vector<std::uint32_t>& mapping) {
    return Gate(
        gate.type(),
        static_cast<std::uint16_t>(mapping[gate.qubit1()]), gate.neg1(),
        static_cast<std::uint16_t>(mapping[gate.qubit2()]), gate.neg2(),
        static_cast<std::uint16_t>(mapping[gate.qubit3()]), gate.neg3(),
        gate.flag()
    );
}

} // namespace core
