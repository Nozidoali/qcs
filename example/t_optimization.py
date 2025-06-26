from pathlib import Path
PROJ_DIR = Path(__file__).parent.parent
qcfile = (PROJ_DIR / "data" / "input" / "qc" / "hadamard_gadgetization.qc").resolve()

import qcs

circuit = qcs.QuantumCircuit.from_file(qcfile)
circuit_opt = qcs.dummy_optimization(circuit)

print("Original Circuit:")
print(circuit.num_t)
print("\nOptimized Circuit:")
print(circuit_opt.num_t)