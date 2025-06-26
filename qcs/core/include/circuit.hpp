#pragma once
#include <vector>
#include <cstdint>
#include "gate.hpp"          // your packed Gate + GateType enum

namespace core {

class QuantumCircuit {
public:
    std::uint32_t        n_qubits = 0;
    std::vector<Gate>    gates;
};

} // namespace core
