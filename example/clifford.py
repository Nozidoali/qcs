import qcs

if __name__ == "__main__":
    circuit = qcs.QuantumCircuit()
    circuit.request_qubits(3)
    circuit.add_h(0)  # Hadamard on qubit 0
    circuit.add_cnot(0, 1)  # CNOT from qubit
    circuit.add_cnot(0, 1)  # CNOT from qubit
    
    tableau = qcs.to_tableau(circuit)    
    print(str(tableau))
    new_circuit = qcs.from_tableau(tableau)
    
    qcs.plot_circuit(circuit, fn="original_circuit.png")
    qcs.plot_circuit(new_circuit, fn="converted_circuit.png")