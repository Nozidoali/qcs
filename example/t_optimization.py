from pathlib import Path
PROJ_DIR = Path(__file__).parent.parent
qcfile = (PROJ_DIR / "data" / "input" / "qc" / "toy.qc").resolve()
# qcfile = (PROJ_DIR / "data" / "input" / "qc" / "hadamard_gadgetization.qc").resolve()

import qcs

circuit = qcs.QuantumCircuit.from_file(qcfile)

py_circuit_opt = qcs.t_count_optimization(circuit, method="TOHPE")

c_circuit_opt = qcs.dummy_optimization(circuit)

# from rich.pretty import pprint
# pprint(c_circuit_opt.to_json())


qcs.plot_circuit(circuit, fn="original_circuit.png")
qcs.plot_circuit(c_circuit_opt, fn="c_optimized_circuit.png")
qcs.plot_circuit(py_circuit_opt, fn="py_optimized_circuit.png")