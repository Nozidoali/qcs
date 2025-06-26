#include "tOptimizer.hpp"
#include <stdexcept>

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

    auto old_tbl = poly_.rows();                         // snapshot
    /* run chosen optimiser */
    //  -- plug in whichever one you need later in optimise()

    // placeholder, optimiser will be applied in optimise()

    out += poly_.clifford_correction(old_tbl, n_).to_circ(false);
    out += poly_.to_circ();
    poly_ = PhasePolynomial(n_);
    emitted_poly_sections_ = true;
}

void TOptimizer::flush_tableau(QuantumCircuit& out) {
    out += tab_.to_row_major().to_circ(true);
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
            tab_.prepend_cx(g.qubit1(), g.qubit2());
            break;

        /* ── T / Td : collect phase-poly rows ─────────── */
        case GateType::T:
        case GateType::Td: {
            std::uint16_t q = g.qubit1();
            /* start new slice if needed */
            if (poly_.rows().empty() && emitted_poly_sections_)
                flush_tableau(out);

            poly_.add_row(tab_.stab(q).z);      // record Z mask
            if (tab_.stab(q).sign) {            // fold sign
                tab_.prepend_s(q);
                tab_.prepend_z(q);
            }
            break;
        }
        default:
            throw std::runtime_error("TOptimizer: unsupported gate");
        }
    }

    /* flush tail */
    flush_poly(out);
    flush_tableau(out);
    return out;
}

/* ---------- stubs for external back-ends (replace by real impl) ---------- */
std::vector<BitVector> TOptimizer::fast_todd(std::vector<BitVector> v,
                                             std::size_t){ return v; }

std::vector<BitVector> TOptimizer::tohpe(std::vector<BitVector> v,
                                         std::size_t){ return v; }

} // namespace core
