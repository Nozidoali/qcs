#pragma once

#include <vector>
#include "gate.hpp"

namespace core {

class QuantumCircuit {
public:
    std::uint32_t n_qubits = 0;
    std::vector<Gate> gates;
    std::vector<std::uint32_t> qubit_mapping;

    QuantumCircuit(std::uint32_t nq = 0);

    QuantumCircuit operator+(const QuantumCircuit& other) const;
    QuantumCircuit& operator+=(const QuantumCircuit& other);

    void append(const QuantumCircuit& sub) { *this += sub; }
    
    std::size_t     request_qubit();
    void            request_qubits(std::size_t count);   // NEW: allocate many at once

    /* ---------- gate helpers used by PhasePolynomial / RowMajorTableau ---------- */
    void add_cnot(std::uint16_t ctrl,  std::uint16_t targ);
    void add_t   (std::uint16_t targ);
    void add_s   (std::uint16_t targ);
    void add_x   (std::uint16_t targ);
    void add_z   (std::uint16_t targ);
    void add_h   (std::uint16_t targ);

    // Utility methods
    std::size_t num_t() const;
    std::size_t num_gates() const;
    std::size_t num_2q() const;
    std::size_t num_internal_h() const;
    std::size_t num_h() const;
    std::size_t first_t() const;
    std::size_t last_t() const;
    std::size_t t_depth_of(std::uint32_t qubit) const;
    std::size_t t_depth() const;

    std::string to_string() const;
};

} // namespace core
