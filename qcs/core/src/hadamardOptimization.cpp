#include "hadamardOptimization.hpp"
#include <iostream>

namespace core {

    

Tableau tableau_from_circ(const QuantumCircuit& circ)
{
    Tableau tab(circ.n_qubits);

    /* -------- 1.  forward scan (Clifford gates only) -------- */
    for (const Gate& g : circ.gates) {
        switch (g.type()) {
        case GateType::H:     tab.prepend_h(g.qubit1());                    break;
        case GateType::X:     tab.prepend_x(g.qubit1());                    break;
        case GateType::Z:     tab.prepend_z(g.qubit1());                    break;
        case GateType::S:
            tab.prepend_s(g.qubit1());
            tab.prepend_z(g.qubit1());                                      break;
        case GateType::CNOT:  tab.prepend_cx(g.qubit1(), g.qubit2());       break;
        default: /* skip Non-Clifford here */                               break;
        }
    }

    /* -------- 2.  reverse scan (handle all gates incl. non-Clifford) --- */
    for (auto it = circ.gates.rbegin(); it != circ.gates.rend(); ++it) {
        const Gate& g = *it;
        switch (g.type()) {
        case GateType::H:     tab.prepend_h(g.qubit1());                    break;
        case GateType::X:     tab.prepend_x(g.qubit1());                    break;
        case GateType::Z:     tab.prepend_z(g.qubit1());                    break;
        case GateType::S:     tab.prepend_s(g.qubit1());                    break;
        case GateType::CNOT:  tab.prepend_cx(g.qubit1(), g.qubit2());       break;

        case GateType::T:
        case GateType::Td:
            implement_pauli_rotation(tab, g.qubit1());                      break;

        case GateType::Toffoli: {
            std::array<std::uint16_t,3> idx{g.qubit1(), g.qubit2(), g.qubit3()};
            implement_tof(tab, idx, /*h_gate=*/true);                       break;
        }
        case GateType::CZ: {   // CCZ  (3-qubit Z gate)
            std::array<std::uint16_t,3> idx{g.qubit1(), g.qubit2(), g.qubit3()};
            implement_tof(tab, idx, /*h_gate=*/false);                      break;
        }

        default:
            throw std::runtime_error("tableau_from_circ: unsupported gate");
        }
    }

    return tab;
}


/* ============================================================= *
 *  2)  Internal-H optimisation pass                              *
 * ============================================================= */
QuantumCircuit internal_h_opt(const QuantumCircuit& c_in)
{
    Tableau tab = tableau_from_circ(c_in);
    std::cout << tab.to_string() << std::endl;

    /*  Build first half circuit */
    QuantumCircuit qc = tab.to_circ(/*inverse=*/false);

    /*  Forward replay over original gates */
    for (const Gate& g : c_in.gates) {
        switch (g.type()) {
        case GateType::H:  tab.prepend_h(g.qubit1());              break;
        case GateType::X:  tab.prepend_x(g.qubit1());              break;
        case GateType::Z:  tab.prepend_z(g.qubit1());              break;
        case GateType::S:
            tab.prepend_s(g.qubit1());
            tab.prepend_z(g.qubit1());
            break;
        case GateType::CNOT:
            tab.prepend_cx(g.qubit1(), g.qubit2());
            break;

        case GateType::T:
        case GateType::Td: {
            QuantumCircuit sub = implement_pauli_rotation(tab, g.qubit1());
            qc = qc + sub;
            break;
        }
        case GateType::Toffoli: {
            std::array<std::uint16_t,3> arr{g.qubit1(), g.qubit2(), g.qubit3()};
            QuantumCircuit sub = implement_tof(tab, arr, true);
            qc = qc + sub;
            break;
        }
        case GateType::CZ: {   // treat as CCZ
            std::array<std::uint16_t,3> arr{g.qubit1(), g.qubit2(), g.qubit3()};
            QuantumCircuit sub = implement_tof(tab, arr, false);
            qc = qc + sub;
            break;
        }
        default:
            throw std::runtime_error("internal_h_opt: unsupported gate");
        }
    }

    /*  Append inverse tableau circuit */
    qc = qc + tab.to_circ(/*inverse=*/true);
    return qc;
}

} // namespace core
