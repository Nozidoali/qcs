import qcs
from rich.pretty import pprint

def gfmult2_impl1() -> qcs.QuantumCircuit:
    circuit = qcs.QuantumCircuit()
    circuit.request_qubits(6)
    
    # Toffoli gates for GF(2) multiplication
    circuit.add_toffoli(0, 2, 4)  # CNOT from qubit 0 and 1 to qubit 2
    circuit.add_toffoli(1, 3, 4)  # CNOT from qubit 0 and 3 to qubit 4
    circuit.add_toffoli(1, 2, 5)  # CNOT from qubit 1 and 3 to qubit 5
    circuit.add_toffoli(0, 3, 5)  # CNOT from qubit 1 and 3 to qubit 5
    circuit.add_toffoli(1, 3, 5)  # CNOT from qubit 1 and 3 to qubit 5
    
    inputs = [f"q{i}" for i in range(4)]
    
    return circuit, inputs

def gfmult2_impl2() -> qcs.QuantumCircuit:
    circuit = qcs.QuantumCircuit()
    circuit.request_qubits(6)
    
    # Toffoli gates for GF(2) multiplication
    circuit.add_clean_toffoli(0, 2, 4)  # CNOT from qubit 0 and 1 to qubit 2
    circuit.add_toffoli(1, 3, 4)  # CNOT from qubit 0 and 3 to qubit 4
    circuit.add_clean_toffoli(1, 2, 5)  # CNOT from qubit 1 and 3 to qubit 5
    circuit.add_toffoli(0, 3, 5)  # CNOT from qubit 1 and 3 to qubit 5
    circuit.add_toffoli(1, 3, 5)  # CNOT from qubit 1 and 3 to qubit 5
    
    inputs = [f"q{i}" for i in range(4)]
    
    return circuit, inputs

def gfmult2_impl3() -> qcs.QuantumCircuit:
    circuit = qcs.QuantumCircuit()
    circuit.request_qubits(6)
    
    # Toffoli gates for GF(2) multiplication
    circuit.add_clean_toffoli(0, 2, 4)  # CNOT from qubit 0 and 1 to qubit 2
    circuit.add_toffoli(1, 3, 4)  # CNOT from qubit 0 and 3 to qubit 4
    circuit.add_clean_toffoli(0, 2, 5)  # CNOT from qubit 1 and 3 to qubit 5
    circuit.add_cnot(0, 1)  # CNOT from qubit 1 and 3 to qubit 5
    circuit.add_cnot(2, 3)  # CNOT from qubit 1 and 3 to qubit 5
    circuit.add_toffoli(1, 3, 5)  # CNOT from qubit 0 and 3 to qubit 4
    circuit.add_cnot(0, 1)  # CNOT from qubit 1 and 3 to qubit 5
    circuit.add_cnot(2, 3)  # CNOT from qubit 1 and 3 to qubit 5
    
    inputs = [f"q{i}" for i in range(4)]
    
    return circuit, inputs


def gfmult2_impl4() -> qcs.QuantumCircuit:
    circuit = qcs.QuantumCircuit()
    circuit.request_qubits(6)
    
    # Toffoli gates for GF(2) multiplication
    circuit.add_clean_toffoli(0, 2, 4)  # CNOT from qubit 0 and 1 to qubit 2
    circuit.add_cnot(4, 5)  # CNOT from qubit 0 and 3 to qubit 4
    circuit.add_toffoli(1, 3, 4)  # CNOT from qubit 1 and 3 to qubit 5
    circuit.add_cnot(0, 1)  # CNOT from qubit 1 and 3 to qubit 5
    circuit.add_cnot(2, 3)  # CNOT from qubit 1 and 3 to qubit 5
    circuit.add_toffoli(1, 3, 5)  # CNOT from qubit 0 and 3 to qubit 4
    circuit.add_cnot(0, 1)  # CNOT from qubit 1 and 3 to qubit 5
    circuit.add_cnot(2, 3)  # CNOT from qubit 1 and 3 to qubit 5
    
    inputs = [f"q{i}" for i in range(4)]
    
    return circuit, inputs

def gfmult2_impl5() -> qcs.QuantumCircuit:
    circuit = qcs.QuantumCircuit()
    circuit.request_qubits(6)
    
    # Toffoli gates for GF(2) multiplication
    circuit.add_cnot(0, 1)  # CNOT from qubit 1 and 3 to qubit 5
    circuit.add_cnot(2, 3)  # CNOT from qubit 1 and 3 to qubit 5
    circuit.add_clean_toffoli(1, 3, 5)  # CNOT from qubit 0 and 3 to qubit 4
    circuit.add_cnot(0, 1)  # CNOT from qubit 1 and 3 to qubit 5
    circuit.add_cnot(2, 3)  # CNOT from qubit 1 and 3 to qubit 5
    circuit.add_clean_toffoli(0, 2, 4)  # CNOT from qubit 0 and 1 to qubit 2
    circuit.add_cnot(4, 5)  # CNOT from qubit 0 and 3 to qubit 4
    circuit.add_toffoli(1, 3, 4)  # CNOT from qubit 1 and 3 to qubit 5
    
    inputs = [f"q{i}" for i in range(4)]
    
    return circuit, inputs

if __name__ == "__main__":
    # circuit, inputs = gfmult2_impl1()
    # open("gfmult2_impl1.qc", "w").write(circuit.to_qc(inputs=inputs))

    # circuit, inputs = gfmult2_impl2()
    # open("gfmult2_impl2.qc", "w").write(circuit.to_qc(inputs=inputs))
    
    # circuit, inputs = gfmult2_impl3()
    # open("gfmult2_impl3.qc", "w").write(circuit.to_qc(inputs=inputs))
    
    # circuit, inputs = gfmult2_impl4()
    # open("gfmult2_impl4.qc", "w").write(circuit.to_qc(inputs=inputs))
    
    # circuit, inputs = gfmult2_impl5()
    # open("gfmult2_impl5.qc", "w").write(circuit.to_qc(inputs=inputs))
    
    # circuit = qcs.QuantumCircuit.from_file("sota.qc")
    # qcs.plot_circuit(circuit, "gfmult2_sota.png")
    
    circuit = qcs.QuantumCircuit.from_file("./data/input/qc/gf_mult2/ours.qc")
    qcs.plot_circuit(circuit, "gfmult2_ours.png")
    circuit = circuit.optimize_cnot_phase_regions()
    qcs.plot_circuit(circuit, "gfmult2_ours_opt.png")
    
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