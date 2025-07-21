from .base import QuantumCircuit
from .gateset import decompose_toffoli

def add_mcx(self, cs: list[int], target: int, ps: list[bool] = [], clean: bool = False) -> None:
    assert len(cs) <= 2, f"MCX only supports 1 or 2 control qubits, got {len(cs)}"
    if len(cs) == 1:
        self.add_cnot(cs[0], target, ps[0])
    elif len(cs) == 2:
        self.add_toffoli(cs[0], cs[1], target, ps[0], ps[1], clean)

def to_basic_gates(self) -> QuantumCircuit:
    _circuit = QuantumCircuit()
    _circuit.n_qubits = self.n_qubits
    for gate in self.gates:
        assert "name" in gate, f"Gate {gate} does not have a 'name' key"
        if gate["name"] == "Tof":
            _circuit.gates.extend(decompose_toffoli(gate["ctrl1"], gate["ctrl2"], gate["target"]))
        else:
            _circuit.add_gate(gate)
    return _circuit.cleanup_dangling_hadamard()
    