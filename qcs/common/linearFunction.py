import numpy as np
from collections import defaultdict

class LinearFunction:
    def __init__(self, n_qubits: int):
        self.n_qubits = n_qubits
        self.matrix = np.eye(n_qubits, dtype=np.uint8)

    @classmethod
    def from_cnot_gates(cls, gates: list[dict], n_qubits: int) -> 'LinearFunction':
        lf = cls(n_qubits)
        for gate in gates:
            if gate["name"] == "CNOT":
                lf._apply_cnot(gate["ctrl"], gate["target"])
        return lf

    def _apply_cnot(self, ctrl: int, target: int):
        self.matrix[target] ^= self.matrix[ctrl]

    @staticmethod
    def to_string(pattern: np.array) -> str:
        """Convert a binary pattern to a string representation."""
        return ''.join(str(bit) for bit in pattern)

def optimize_cnot_phase_block(gates: list[dict], n_qubits: int) -> list[dict]:
    lf = LinearFunction(n_qubits)
    
    term_to_phase: dict[str, int] = defaultdict(int)
    
    for gate in gates:
        if gate["name"] in {"T", "Tdg", "S", "Z"}:
            phase: dict[str, int] = {
                "T": 1, "Tdg": 7, "S": 2, "Z": 4
            }
            q = gate["target"]
            
            term = lf.matrix[q].copy()
            term_str = LinearFunction.to_string(term)
            if term_str not in term_to_phase:
                term_to_phase[term_str] = 0
            term_to_phase[term_str] += phase[gate["name"]]
        elif gate["name"] == "CNOT":
            ctrl = gate["ctrl"]
            target = gate["target"]
            lf._apply_cnot(ctrl, target)
        else:
            raise ValueError(f"Unsupported gate: {gate['name']}")
    
    for term, phase in term_to_phase.items():
        print(f"Term: {term}, Phase: {phase}")
        
    return {}

def main():
    print("=== Test: LinearFunction from CNOT gates ===")
    gates = [
        {"name": "CNOT", "ctrl": 0, "target": 1},
        {"name": "S", "target": 2},
        {"name": "CNOT", "ctrl": 1, "target": 2},
        {"name": "T", "target": 0},
        {"name": "Tdg", "target": 1},
        {"name": "CNOT", "ctrl": 2, "target": 0},
        {"name": "Z", "target": 0}
    ]
    n = 3
    lf = LinearFunction.from_cnot_gates(gates, n)

    optimize_cnot_phase_block(gates, n)

if __name__ == "__main__":
    main()
