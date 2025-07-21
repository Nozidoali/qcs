from .base import QuantumCircuit

from .metrics import *
QuantumCircuit.num_t = num_t
QuantumCircuit.num_2q = num_2q
QuantumCircuit.num_h = num_h
QuantumCircuit.num_internal_h = num_internal_h
QuantumCircuit.t_depth = t_depth
QuantumCircuit.t_depth_of = t_depth_of
QuantumCircuit.num_gates = num_gates

from .gateset import *
QuantumCircuit.add_clean_toffoli = add_clean_toffoli

from .decomposition import *
QuantumCircuit.add_mcx = add_mcx
QuantumCircuit.to_basic_gates = to_basic_gates

from .toffoliGadgetization import *
QuantumCircuit.gadgetize_toffoli = gadgetize_toffoli

from .hadamardGadgetization import *
QuantumCircuit.hadamard_gadgetization = hadamard_gadgetization

from .phaseCNOTSynthesis import *
QuantumCircuit.optimize_cnot_phase_regions = optimize_cnot_phase_regions
QuantumCircuit.optimize_cnot_regions = optimize_cnot_regions

from .cleanupDangling import *
QuantumCircuit.cleanup_dangling_hadamard = cleanup_dangling_hadamard
QuantumCircuit.cleanup = cleanup

from .io import *
QuantumCircuit.from_truth_table = from_truth_table
QuantumCircuit.from_qasm = from_qasm
QuantumCircuit.from_file = from_file
QuantumCircuit.to_qasm = to_qasm
QuantumCircuit.to_qc = to_qc
QuantumCircuit.to_json = to_json

from .zxCalculus import *
QuantumCircuit.run_zx = run_zx

from .fastTODD import *
QuantumCircuit.fast_todd_optimize = fast_todd_optimize

from .transformations import *
QuantumCircuit.map_qubit = map_qubit
QuantumCircuit.swap_qubits = swap_qubits