from qiskit import QuantumCircuit as QiskitCircuit
from qiskit_aer import AerSimulator


def simulate_with_input_string(qcs_circuit, input_pattern: str, n_shots: int) -> QiskitCircuit:
    n = qcs_circuit.n_qubits
    qc = QiskitCircuit(n)
    
    for i in range(n):
        if input_pattern[n-i-1] == "1":
            qc.x(i)
    for gate in qcs_circuit.gates:
        name = gate["name"]
        if name == "CNOT":
            qc.cx(gate["ctrl"], gate["target"])
        elif name == "CZ":
            qc.cz(gate["ctrl"], gate["target"])
        elif name == "Tof":
            qc.ccx(gate["ctrl1"], gate["ctrl2"], gate["target"])
        elif name == "X":
            qc.x(gate["target"])
        elif name == "Z":
            qc.z(gate["target"])
        elif name == "HAD":
            qc.h(gate["target"])
        elif name == "S":
            qc.s(gate["target"])
        elif name == "Sdg":
            qc.sdg(gate["target"])
        elif name == "T":
            qc.t(gate["target"])
        elif name == "Tdg":
            qc.tdg(gate["target"])
        elif name == "Swap":
            qc.swap(gate["q0"], gate["q1"])
        else:
            raise ValueError(f"Unsupported gate: {name}")
        
    qc.measure_all()
    ideal_simulator = AerSimulator(method="statevector")
    counts = ideal_simulator.run(qc, shots=n_shots).result().get_counts()
    return counts