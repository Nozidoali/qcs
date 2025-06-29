#include "tOptimizer.hpp"
#include <stdexcept>
#include <iostream>

namespace core {

QuantumCircuit optimize_t_gates(const QuantumCircuit& circ) {
    std::size_t n = circ.n_qubits;  // or `circ.get_num_qubits()`
    QuantumCircuit out; out.request_qubits(n);
    
    auto it = circ.gates.begin();
    
    // Skip initial gates until the first T or Td gate is seen
    while (it != circ.gates.end()) {
        if (it->type() == GateType::T || it->type() == GateType::Td) {
            break;  // Found the first T gate
        }
        out.gates.push_back(*it);
        ++it;
    }
    
    // If we reached the end without finding a T gate, return the initial circuit
    if (it == circ.gates.end()) {
        // No T gates found, return the initial circuit
        return out;
    }
    
    std::vector<PhasePolynomial> phase_polynomials;
    std::vector<ColumnMajorTableau> tableau_vec;

    ColumnMajorTableau tab(n);
    PhasePolynomial poly(n);

    for (; it != circ.gates.end(); ++it) {
        const Gate& g = *it;
        switch (g.type()) {
        case GateType::H:
            if (!poly.empty()) {
                phase_polynomials.push_back(poly);
                poly = PhasePolynomial(n);
            }
            tab.prepend_h(g.qubit1());
            break;
        case GateType::X:
            tab.prepend_x(g.qubit1());
            break;
        case GateType::Z:
            tab.prepend_z(g.qubit1());
            break;
        case GateType::S: {
            auto q = g.qubit1();
            tab.prepend_s(q); tab.prepend_z(q);
            break;
        }
        case GateType::CNOT:
            tab.prepend_cx(g.qubit2(), g.qubit1());
            break;

        case GateType::T:
        case GateType::Td: {
            auto q = g.qubit1();
            if (poly.empty() && !phase_polynomials.empty()) {
                tableau_vec.push_back(tab);
                tab = ColumnMajorTableau(n);
            }
            poly.add_row(tab.stabilizer(q).z);
            if (tab.stabilizer(q).sign) {
                tab.prepend_s(q);
                tab.prepend_z(q);
            }
            break;
        }

        default:
            throw std::runtime_error("optimize_t_gates: unsupported gate");
        }
    }

    if (!poly.empty()) phase_polynomials.push_back(poly);
    tableau_vec.push_back(tab);

    std::cout << "Phase polynomials: " << phase_polynomials.size() << '\n';
    std::cout << "Tableau vectors: " << tableau_vec.size() << '\n';

    // Compose final circuit
    for (std::size_t i = 0; i < phase_polynomials.size(); ++i) {
        auto& p = phase_polynomials[i];
        auto original = p.get_rows();
        tohpe(original, p.get_rows(), n);  // Apply TOHPE in-place
        out += p.clifford_correction(original, n).to_circ();
        out += p.to_circ();
        if (i < tableau_vec.size()) {
            out += tableau_vec[i].to_row_major().to_circ(true);
        }
    }

    return out;
}


} // namespace core
