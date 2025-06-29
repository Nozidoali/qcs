import qcs
from rich.pretty import pprint

if __name__ == "__main__":
    circuit = qcs.QuantumCircuit()
    circuit.request_qubits(3)
    circuit.add_cnot(0, 1)  # Hadamard on qubit 0
    circuit.add_cnot(0, 2)  # Hadamard on qubit 0
    circuit.add_cnot(2, 0)  # Hadamard on qubit 0
    circuit.add_cnot(2, 1)  # Hadamard on qubit 0
    
    tableau = qcs.to_tableau(circuit)
    print(tableau)
    circuit_new = qcs.from_tableau(tableau)
    pprint(circuit_new.to_json())