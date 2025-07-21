from .base import QuantumCircuit

def gadgetize_toffoli(self) -> QuantumCircuit:
    clean_qubits = {i: True for i in range(self.n_qubits)}
    
    n = len(self.gates)

    _circuit = QuantumCircuit()
    _circuit.n_qubits = self.n_qubits
    
    for i in range(n):
        g = self.gates[i]
        target = g["target"]
        
        if g["name"] == "Tof":
            c1, c2 = g["ctrl1"], g["ctrl2"]
            if clean_qubits[target]:
                _circuit.add_clean_toffoli(c1, c2, target)
            else:
                _circuit.add_toffoli(c1, c2, target)            
        else:
            _circuit.add_gate(g)
            target = g["target"]
            clean_qubits[target] = False
    return _circuit