#include "toffoliOptimization.hpp"

namespace core {

/* local cat helper */
static void concat(QuantumCircuit& dst, const QuantumCircuit& src) {
    dst.gates.insert(dst.gates.end(), src.gates.begin(), src.gates.end());
}

/* ------------------------------------------------------------- *
 *        implement_tof                                          *
 * ------------------------------------------------------------- */
QuantumCircuit implement_tof(RowMajorTableau& tab,
                             const std::array<std::uint16_t,3>& cols,
                             bool h_gate)
{
    std::size_t nq = tab.n_qubits();
    QuantumCircuit qc;  qc.request_qubits(nq);

    /* -- 1. three Pauli rotations to prepare columns  ------------ */
    concat(qc, implement_pauli_rotation(tab, cols[0]));                 // ctrl1
    concat(qc, implement_pauli_rotation(tab, cols[1]));                 // ctrl2

    std::size_t col_targ = cols[2] + (h_gate ? nq : 0);                 // destab if X
    concat(qc, implement_pauli_rotation(tab, col_targ));

    /* -- 2. build intermediary Pauli products -------------------- */
    PauliProduct p0 = tab.extract_pauli_product(cols[0]);
    PauliProduct p1 = tab.extract_pauli_product(cols[1]);
    PauliProduct p2 = tab.extract_pauli_product(col_targ);

    /* helper lambda: XOR z masks and update sign, then emit Z-rot */
    auto do_zrot = [&](PauliProduct& pa, const PauliProduct& pb) {
        pa.z.xor_with(pb.z);
        pa.sign ^= pb.sign ^ true;
        concat(qc, implement_pauli_z_rotation_from_pauli_product(tab, pa));
    };

    /* sequence exactly mirrors Python */
    do_zrot(p0, p1);
    do_zrot(p0, p2);
    do_zrot(p0, p1);
    do_zrot(p1, p2);

    return qc;
}

} // namespace core
