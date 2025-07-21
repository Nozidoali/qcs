from pathlib import Path
PROJ_DIR = Path(__file__).parent.parent
qcfile = (PROJ_DIR / "data" / "input" / "qc" / "toy.qc").resolve()
# qcfile = (PROJ_DIR / "data" / "input" / "qc" / "hadamard_gadgetization.qc").resolve()

import qcs

circuit = qcs.QuantumCircuit.from_file(qcfile)

py_circuit_opt = qcs.t_count_optimization(circuit, method="TOHPE")

c_circuit_opt = qcs.t_opt(circuit)

from rich.pretty import pprint
pprint(c_circuit_opt.to_json())

qcs.plot_circuit(circuit, fn="original_circuit.png")
qcs.plot_circuit(c_circuit_opt, fn="c_optimized_circuit.png")
qcs.plot_circuit(py_circuit_opt, fn="py_optimized_circuit.png")

circuit = circuit.optimize_cnot_regions()
# qcs.plot_circuit(circuit, "gfmult2_ours_opt.png")

print(circuit.num_t)

print(" a   b  | output")
print("-----------")
for a in range(4):
    for b in range(4):
        # Prepare input string: a (2 bits), b (2 bits), ancilla (2 bits, set to 0)
        input_bits = f"00{b:02b}{a:02b}"
        # input_bits = input_bits[::-1]
        counts = qcs.simulate_with_input_string(circuit, input_bits, n_shots=1024)
        # There should be only one output with all shots
        assert len(counts) == 1, f"Unexpected counts for input {input_bits}: {counts}"
        output = next(iter(counts))
        print(f" {input_bits} | {output}")