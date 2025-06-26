from pathlib import Path
PROJ_DIR = Path(__file__).parent.parent
qcfile = (PROJ_DIR / "data" / "input" / "qc" / "hadamard_gadgetization.qc").resolve()

import qcs

circuit = qcs.QuantumCircuit.from_file(qcfile)
circuit_opt = qcs.dummy_optimization(circuit)

from rich.pretty import pprint

pprint(circuit_opt.to_json())


qcs.plot_circuit(circuit, fn="original_circuit.png")
qcs.plot_circuit(circuit_opt, fn="optimized_circuit.png")