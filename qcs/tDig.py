from qcs.common import QuantumCircuit
from qcs.common.quantumCircuit.fastTODD import fast_todd_optimize
from qcs.visualization import plot_circuit

def iterative_gadgetization(circuit: QuantumCircuit) -> QuantumCircuit:
    clean_qubits = {i: True for i in range(circuit.n_qubits)}
    
    n = len(circuit.gates)

    _circuit = QuantumCircuit()
    _circuit.n_qubits = circuit.n_qubits
        
    for i in range(n):
        g = circuit.gates[i]
                
        target = g["target"]
        
        if g["name"] == "Tof":
            c1, c2 = g["ctrl1"], g["ctrl2"]
            
            if clean_qubits[target]:
                # we don't need to gadgetize it if the qubit is clean
                _circuit.add_clean_toffoli(c1, c2, target)
                clean_qubits[target] = False
                continue
            
            circuit_gadgetize = _circuit.copy()
            ancilla = circuit_gadgetize.request_qubit()
            circuit_gadgetize.add_clean_toffoli(c1, c2, ancilla)
            circuit_gadgetize = fast_todd_optimize(circuit_gadgetize)
            t_gadgetize = circuit_gadgetize.num_t
            
            circuit_no_gadgetize = _circuit.copy()
            circuit_no_gadgetize.add_gate(g)
            circuit_no_gadgetize = fast_todd_optimize(circuit_no_gadgetize)
            t_no_gadgetize = circuit_no_gadgetize.num_t
            
            # predict the T gates by looking at the Toffoli gates after this 
            future_gain_no_gadgetize = 0
            phase_poly_nomial_qubits = set()
            phase_poly_nomial_qubits.add(target)
            phase_poly_nomial_qubits.add(c1)
            phase_poly_nomial_qubits.add(c2)
            for j in range(i + 1, n):
                future_gate = circuit.gates[j]
                if future_gate["name"] == "Tof":
                    if future_gate["ctrl1"] in phase_poly_nomial_qubits:
                        future_gain_no_gadgetize += 1
                    if future_gate["ctrl2"] in phase_poly_nomial_qubits:
                        future_gain_no_gadgetize += 1
                    if future_gate["target"] in phase_poly_nomial_qubits:
                        future_gain_no_gadgetize += 2
                    phase_poly_nomial_qubits.add(future_gate["target"])
                    phase_poly_nomial_qubits.add(future_gate["ctrl1"])
                if future_gate["name"] == "CNOT":
                    if future_gate["target"] in phase_poly_nomial_qubits:
                        future_gain_no_gadgetize += 2
                    if future_gate["ctrl"] in phase_poly_nomial_qubits:
                        future_gain_no_gadgetize += 1

                    phase_poly_nomial_qubits.add(future_gate["target"])
            
            # print(f"Cost of gadgetizing Toffoli gate {i} ({target}, {c1}, {c2}):")
            # print(f"  Gadgetize: {t_gadgetize} T gates")
            # print(f"  No gadgetize: {t_no_gadgetize} T gates")
            # print(f"  Future gain if no gadgetize: {future_gain_no_gadgetize} T gates")
            
            if t_gadgetize + future_gain_no_gadgetize < t_no_gadgetize:
                ancilla = _circuit.request_qubit()
                _circuit.add_clean_toffoli(c1, c2, ancilla)
                if ancilla != target:
                    _circuit.swap_qubits(target, ancilla)
            else:
                _circuit.add_toffoli(c1, c2, target)
                
            # plot_circuit(_circuit, f"gadgetized_tof_{i}.png")
        else:
            _circuit.add_gate(g)
        clean_qubits[target] = False
    _circuit = fast_todd_optimize(_circuit)
    # plot_circuit(_circuit, "final_circuit.png")
    return fast_todd_optimize(_circuit)