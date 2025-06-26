#include "gate.hpp"
#include <sstream>

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

std::string Gate::to_string() const {
    std::ostringstream oss;
    oss << "Gate(type=" << gate_type_to_string(type())
        << ", q1=" << qubit1() << (neg1() ? " negated" : "")
        << ", q2=" << qubit2() << (neg2() ? " negated" : "")
        << ", q3=" << qubit3() << (neg3() ? " negated" : "")
        << ", flag=" << flag() << ")";
    return oss.str();
}

std::string gate_type_to_string(GateType type) {
    switch (type) {
        case GateType::X:      return "X";
        case GateType::Z:      return "Z";
        case GateType::H:      return "H";
        case GateType::CNOT:   return "CNOT";
        case GateType::T:      return "T";
        case GateType::Td:     return "Td";
        case GateType::S:      return "S";
        case GateType::Sd:     return "Sd";
        case GateType::Toffoli:return "Toffoli";
        case GateType::Swap:   return "Swap";
        case GateType::CZ:     return "CZ";
        default:               return "Unknown";
    }
}

} // namespace core
