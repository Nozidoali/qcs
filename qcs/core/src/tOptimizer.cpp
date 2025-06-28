#include "tOptimizer.hpp"
#include <stdexcept>
#include <iostream>

namespace core {

/* ---------- ctor ---------- */
TOptimizer::TOptimizer(std::size_t n_qubits)
    : n_(n_qubits),
      tab_(n_qubits),
      poly_(n_qubits)
{}

/* ---------- flush helpers ---------- */
void TOptimizer::flush_poly(QuantumCircuit& out) {
    if (poly_.rows().empty()) return;

    std::vector<BitVector> old_tableau = poly_.rows();

    // print the phase polynomial for debugging
    for (const auto& row : old_tableau) {
        std::cout << row.to_string() << std::endl;
    }

    // use tohpe to optimise the phase polynomial
    tohpe(old_tableau, poly_.get_rows(), n_); 

    std::cout << "Optimised Phase Polynomial:" << std::endl;
    for (const auto& row : poly_.rows()) {
        std::cout << row.to_string() << std::endl;
    }

    out += poly_.clifford_correction(old_tableau, n_).to_circ();
    out += poly_.to_circ();

    // reset the phase polynomial
    poly_ = PhasePolynomial(n_);
    emitted_poly_sections_ = true;
}

void TOptimizer::flush_tableau(QuantumCircuit& out) {
    out += tab_.to_row_major().to_circ(true);

    // we reset the tableau after flushing
    tab_ = ColumnMajorTableau(n_);
}

/* ================================================================ *
 *  main entry                                                      *
 * ================================================================ */
QuantumCircuit TOptimizer::optimize(const QuantumCircuit& circ,
                                    const std::string& optimiser)
{
    QuantumCircuit out; out.request_qubits(n_);
    bool first_t_seen = false;
    for (std::size_t idx = 0; idx < circ.gates.size(); ++idx) {

        const Gate& g = circ.gates[idx];

        /* copy gates prior to first T untouched */
        if (!first_t_seen) {
            if (is_t_gate(g)) first_t_seen = true;
            if (!first_t_seen) { out.gates.push_back(g); continue; }
        }

        /* ---------- process post-T slice gates ---------- */
        switch (g.type()) {
        /* ── Clifford ────────────────────────────────── */
        case GateType::H:
            flush_poly(out);
            flush_tableau(out);
            tab_.prepend_h(g.qubit1());
            break;

        case GateType::X:  tab_.prepend_x(g.qubit1()); break;
        case GateType::Z:  tab_.prepend_z(g.qubit1()); break;

        case GateType::S: {
            std::uint16_t q = g.qubit1();
            tab_.prepend_s(q); tab_.prepend_z(q);
            break;
        }
        case GateType::CNOT:
            tab_.prepend_cx(g.qubit2(), g.qubit1());
            break;

        /* ── T / Td : collect phase-poly rows ─────────── */
        case GateType::T:
        case GateType::Td: {
            std::uint16_t q = g.qubit1();
            /* start new slice if needed */
            if (poly_.rows().empty() && emitted_poly_sections_)
                flush_tableau(out);

            poly_.add_row(tab_.stabilizer(q).z);      // record Z mask
            if (tab_.stabilizer(q).sign) {            // fold sign
                tab_.prepend_s(q);
                tab_.prepend_z(q);
            }
            break;
        }
        default:
            throw std::runtime_error("TOptimizer: unsupported gate");
        }

        // print the table for debugging
        // std::cout << "Gate: " << g.to_string() << std::endl;
        // std::cout << tab_.to_row_major().to_string() << std::endl;
    }

    /* flush tail */
    if (!poly_.empty()) flush_poly(out);
    flush_tableau(out);
    return out;
}

} // namespace core
