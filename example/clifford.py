import qcs

if __name__ == "__main__":
    circuit = qcs.QuantumCircuit()
    circuit.request_qubits(2)
    circuit.add_cnot(0, 1)  # Hadamard on qubit 0
    circuit.add_h(0)        # Hadamard on qubit 0
    
    tableau = qcs.to_tableau(circuit)
    print(tableau)
