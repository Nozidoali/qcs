#include "pauliOptimization.hpp"

namespace core {

/* ------------------------------------------------------------- *
 *  utility: dst += src (concatenate gate arrays)                 *
 * ------------------------------------------------------------- */
static inline void concat(QuantumCircuit& dst, const QuantumCircuit& src)
{
    dst.gates.insert(dst.gates.end(), src.gates.begin(), src.gates.end());
}

/* ------------------------------------------------------------- *
 *  1) Z-rotation from explicit PauliProduct                      *
 * ------------------------------------------------------------- */
QuantumCircuit implement_pauli_z_rotation_from_pauli_product(
        const RowMajorTableau& tab, const PauliProduct& p)
{
    std::size_t nq = tab.n_qubits();
    QuantumCircuit qc;  qc.request_qubits(nq);
    QuantumCircuit blk; blk.request_qubits(nq);

    std::size_t pivot = p.z.get_first_one();

    /* build CX fan-in/out */
    for (std::size_t j = 0; j < nq; ++j)
        if (p.z.get(j) && j != pivot)
            blk.add_cnot(static_cast<std::uint16_t>(j),
                         static_cast<std::uint16_t>(pivot));

    concat(qc, blk);
    qc.add_t(static_cast<std::uint16_t>(pivot));

    if (p.sign) {
        qc.add_s(static_cast<std::uint16_t>(pivot));
        qc.add_z(static_cast<std::uint16_t>(pivot));
    }
    concat(qc, blk);
    return qc;
}

/* ------------------------------------------------------------- *
 *  2) Z-rotation specified by tableau column                     *
 * ------------------------------------------------------------- */
QuantumCircuit implement_pauli_z_rotation(const RowMajorTableau& tab, std::size_t col)
{
    std::size_t nq = tab.n_qubits();
    QuantumCircuit qc;  qc.request_qubits(nq);
    QuantumCircuit blk; blk.request_qubits(nq);

    /* find stabiliser row with Z in column */
    std::size_t pivot = 0;
    while (pivot < nq && !tab.z_row(pivot).get(col)) ++pivot;

    for (std::size_t j = 0; j < nq; ++j)
        if (tab.z_row(j).get(col) && j != pivot)
            blk.add_cnot(static_cast<std::uint16_t>(j),
                         static_cast<std::uint16_t>(pivot));

    concat(qc, blk);
    qc.add_t(static_cast<std::uint16_t>(pivot));

    if (tab.sign_bit(col)) {
        qc.add_s(static_cast<std::uint16_t>(pivot));
        qc.add_z(static_cast<std::uint16_t>(pivot));
    }
    concat(qc, blk);
    return qc;
}

/* ------------------------------------------------------------- *
 *  3) Full Pauli rotation on tableau column (mutates tab)        *
 * ------------------------------------------------------------- */
QuantumCircuit implement_pauli_rotation(RowMajorTableau& tab, std::size_t col)
{
    std::size_t nq = tab.n_qubits();
    QuantumCircuit qc;  qc.request_qubits(nq);

    /* identify pivot row with an X in column */
    bool has_x = false;
    std::size_t pivot = 0;
    for (; pivot < nq; ++pivot)
        if (tab.x_row(pivot).get(col)) { has_x = true; break; }

    if (has_x) {
        /* clear other Xs via CX fan-out */
        for (std::size_t j = 0; j < nq; ++j)
            if (tab.x_row(j).get(col) && j != pivot) {
                tab.append_cx(pivot, j);
                qc.add_cnot(static_cast<std::uint16_t>(pivot),
                            static_cast<std::uint16_t>(j));
            }

        /* add S if pivot already has Z */
        if (tab.z_row(pivot).get(col)) {
            tab.append_s(pivot);
            qc.add_s(static_cast<std::uint16_t>(pivot));
        }

        /* convert X→Z via H */
        tab.append_h(pivot);
        qc.add_h(static_cast<std::uint16_t>(pivot));
    }

    /* now perform pure-Z rotation */
    concat(qc, implement_pauli_z_rotation(tab, col));
    return qc;
}

} // namespace core
