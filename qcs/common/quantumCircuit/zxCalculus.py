import pyzx as zx
from .base import QuantumCircuit

def run_zx(self) -> QuantumCircuit:
    circuit = zx.Circuit.from_qasm(self.to_qasm())
    graph = circuit.to_graph()
    zx.simplify.full_reduce(graph, quiet=True)
    circuit = zx.extract_circuit(graph, up_to_perm=False)
    circuit = circuit.to_basic_gates()
    circuit = circuit.split_phase_gates()
    return QuantumCircuit.from_zx_circuit(circuit)
