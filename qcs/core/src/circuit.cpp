#include "circuit.hpp"
#include <algorithm>
#include <unordered_map>
#include <vector>
#include <stdexcept>

namespace core {

QuantumCircuit::QuantumCircuit(std::uint32_t nq) : n_qubits(nq), qubit_mapping(nq) {
    for (std::uint32_t i = 0; i < nq; ++i)
        qubit_mapping[i] = i;
}


/* ---------------------------------------------------------- *
 *  Qubit allocation helpers                                  *
 * ---------------------------------------------------------- */
std::size_t QuantumCircuit::request_qubit() {
    std::uint32_t id = n_qubits++;
    qubit_mapping.push_back(id);
    return id;
}

void QuantumCircuit::request_qubits(std::size_t count) {
    for (std::size_t i = 0; i < count; ++i) {
        request_qubit();                // re-uses existing single-qubit method
    }
}

/* ---------------------------------------------------------- *
 *  Gate creation shortcuts                                   *
 * ---------------------------------------------------------- */
void QuantumCircuit::add_cnot(std::uint16_t ctrl, std::uint16_t targ) {
    gates.emplace_back(GateType::CNOT, ctrl, false, targ);
}

void QuantumCircuit::add_t(std::uint16_t targ) {
    gates.emplace_back(GateType::T, targ);
}

void QuantumCircuit::add_s(std::uint16_t targ) {
    gates.emplace_back(GateType::S, targ);
}

void QuantumCircuit::add_x(std::uint16_t targ) {
    gates.emplace_back(GateType::X, targ);
}

void QuantumCircuit::add_z(std::uint16_t targ) {
    gates.emplace_back(GateType::Z, targ);
}

void QuantumCircuit::add_h(std::uint16_t targ) {
    gates.emplace_back(GateType::H, targ);
}

QuantumCircuit QuantumCircuit::operator+(const QuantumCircuit& other) const {
    QuantumCircuit combined;

    // Step 1: collect all unique global indices from both mappings
    std::unordered_map<std::uint32_t, std::uint32_t> global_to_combined;
    std::vector<std::uint32_t> combined_global_indices;

    auto register_qubits = [&](const std::vector<std::uint32_t>& mapping) {
        for (std::uint32_t g : mapping) {
            if (global_to_combined.find(g) == global_to_combined.end()) {
                global_to_combined[g] = static_cast<std::uint32_t>(combined_global_indices.size());
                combined_global_indices.push_back(g);
            }
        }
    };

    register_qubits(this->qubit_mapping);
    register_qubits(other.qubit_mapping);

    combined.n_qubits = static_cast<std::uint32_t>(combined_global_indices.size());

    // Step 2: create combined qubit mapping
    for (std::uint32_t g : this->qubit_mapping) {
        auto it = global_to_combined.find(g);
        if (it == global_to_combined.end()) {
            throw std::runtime_error("Missing global index in this->qubit_mapping");
        }
        combined.qubit_mapping.push_back(it->second);
    }
    for (std::uint32_t g : other.qubit_mapping) {
        auto it = global_to_combined.find(g);
        if (it == global_to_combined.end()) {
            throw std::runtime_error("Missing global index in other.qubit_mapping");
        }
        combined.qubit_mapping.push_back(it->second);
    }

    // Step 3: remap and append gates from both circuits
    auto remap_and_append = [&](const QuantumCircuit& circuit) {
        std::vector<std::uint32_t> local_to_combined(circuit.n_qubits);
        for (std::size_t i = 0; i < circuit.n_qubits; ++i) {
            std::uint32_t g = circuit.qubit_mapping[i];
            auto it = global_to_combined.find(g);
            if (it == global_to_combined.end()) {
                throw std::runtime_error("Mapping failure in remap_and_append()");
            }
            local_to_combined[i] = it->second;
        }

        for (const auto& g : circuit.gates) {
            combined.gates.push_back(map_qubits(g, local_to_combined));
        }
    };

    remap_and_append(*this);
    remap_and_append(other);

    return combined;
}

QuantumCircuit& QuantumCircuit::operator+=(const QuantumCircuit& other)
{
    /* 1 . ensure we have at least as many qubits as other */
    if (other.n_qubits > n_qubits) {
        for (std::uint32_t q = n_qubits; q < other.n_qubits; ++q) {
            qubit_mapping.push_back(q);          // identity map for fresh qubits
        }
        n_qubits = other.n_qubits;
    }

    /* 2 . simply splice the gates vector (fast, no per-gate copy) */
    gates.insert(gates.end(), other.gates.begin(), other.gates.end());
    return *this;
}

std::size_t QuantumCircuit::num_t() const {
    return std::count_if(gates.begin(), gates.end(), [](const Gate& g) {
        return g.type() == GateType::T || g.type() == GateType::Td;
    });
}

std::size_t QuantumCircuit::num_gates() const {
    return gates.size();
}

std::size_t QuantumCircuit::num_2q() const {
    return std::count_if(gates.begin(), gates.end(), [](const Gate& g) {
        return g.type() == GateType::CNOT || g.type() == GateType::CZ;
    });
}

std::size_t QuantumCircuit::num_h() const {
    return std::count_if(gates.begin(), gates.end(), [](const Gate& g) {
        return g.type() == GateType::H;
    });
}

std::size_t QuantumCircuit::first_t() const {
    for (std::size_t i = 0; i < gates.size(); ++i) {
        if (gates[i].type() == GateType::T || gates[i].type() == GateType::Td)
            return i;
    }
    return gates.size();
}

std::size_t QuantumCircuit::last_t() const {
    if (num_t() == 0) return 0;
    for (std::size_t i = gates.size(); i-- > 0;) {
        if (gates[i].type() == GateType::T || gates[i].type() == GateType::Td)
            return i + 1;
    }
    return 0;
}

std::size_t QuantumCircuit::num_internal_h() const {
    std::size_t first = first_t();
    std::size_t last = last_t();
    std::size_t count = 0;

    for (std::size_t i = first; i < last; ++i) {
        if (gates[i].type() == GateType::H) {
            count++;
        }
    }

    return count;
}

std::size_t QuantumCircuit::t_depth_of(std::uint32_t qubit) const {
    std::size_t count = 0;
    for (const auto& g : gates) {
        if ((g.type() == GateType::T || g.type() == GateType::Td) && g.qubit1() == qubit) {
            count++;
        }
    }
    return count;
}

std::size_t QuantumCircuit::t_depth() const {
    if (num_t() == 0) return 0;
    std::size_t max_d = 0;
    for (std::uint32_t q = 0; q < n_qubits; ++q) {
        max_d = std::max(max_d, t_depth_of(q));
    }
    return max_d;
}

} // namespace core
