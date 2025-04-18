from logicNetwork import LogicNetwork
from quantumCircuit import QuantumCircuit

def extract(network: LogicNetwork) -> QuantumCircuit:
    circuit = QuantumCircuit()
    qubits = {}
    for i, input in enumerate(network.inputs):
        qubits[input] = circuit.request_qubit()
    for node, gate in network.gates.items():
        qubits[node] = circuit.request_qubit()
        if gate.is_and:
            ctrl1 = qubits[gate.inputs[0]]
            ctrl2 = qubits[gate.inputs[1]]
            target = qubits[node]
            p1, p2 = gate.data["p1"], gate.data["p2"]
            circuit.add_toffoli(ctrl1, ctrl2, target, p1, p2, True)
        else:
            ctrl = qubits[gate.inputs[0]]
            target = qubits[gate.output]
            circuit.add_cnot(ctrl, target)
    return circuit