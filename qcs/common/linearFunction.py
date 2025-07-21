import numpy as np
from collections import defaultdict

class LinearFunction:
    def __init__(self, n_qubits: int):
        self.n_qubits = n_qubits
        self.matrix = np.eye(n_qubits, dtype=np.uint8)

    def apply_cnot(self, ctrl: int, target: int):
        self.matrix[target] ^= self.matrix[ctrl]
        
    def apply_gates(self, gates: list[dict]):
        for gate in gates:
            if gate["name"] == "CNOT":
                self.apply_cnot(gate["ctrl"], gate["target"])
            else:
                raise ValueError(f"Unsupported gate: {gate['name']}")

    @staticmethod
    def to_string(pattern: np.array) -> str:
        """Convert a binary pattern to a string representation."""
        return ''.join(str(bit) for bit in pattern)

def is_one_hot_matrix(mat: np.ndarray) -> bool:
    return all(np.count_nonzero(row) == 1 for row in mat)

def is_diagonal_matrix(mat: np.ndarray) -> bool:
    return np.all(mat == np.eye(len(mat), dtype=np.uint8))

def append_phase(gates: list[dict], phase: int, best_index: int) -> None:
    if phase == 1:
        gates.append({"name": "T", "target": best_index})
    elif phase == 2:
        gates.append({"name": "S", "target": best_index})
    elif phase == 3:
        gates.extend([{"name": "S", "target": best_index}, {"name": "T", "target": best_index}])
    elif phase == 4:
        gates.append({"name": "Z", "target": best_index})
    elif phase == 5:
        gates.extend([
            {"name": "Z", "target": best_index},
            {"name": "T", "target": best_index},
        ])
    elif phase == 6:
        gates.extend([
            {"name": "Z", "target": best_index},
            {"name": "S", "target": best_index},
        ])
    elif phase == 7:
        gates.append({"name": "T", "target": best_index})
        gates.append({"name": "S", "target": best_index})
        gates.append({"name": "Z", "target": best_index})
    # phase == 0 is skipped
    

def synthesize_parity_strings(term_to_phase: dict[str, int], n_qubits: int) -> list[dict]:
    """Synthesize a list of CNOT + phase gates to produce the required parity strings."""
    current_basis = np.eye(n_qubits, dtype=np.uint8)
    gates = []

    # Copy to avoid mutating input
    term_to_phase = dict(term_to_phase)

    def hamming_distance(a, b):
        return np.count_nonzero(a != b)

    while term_to_phase:
        best_term = None
        best_index = None
        best_distance = float('inf')

        # Try to find the closest match to the current basis
        for term_str in term_to_phase:
            term = np.array([int(b) for b in term_str], dtype=np.uint8)
            for i in range(n_qubits):
                dist = hamming_distance(current_basis[i], term)
                if dist < best_distance:
                    best_distance = dist
                    best_term = term
                    best_index = i

        assert best_term is not None

        # Synthesize CNOTs to transform current_basis[best_index] to best_term
        src = current_basis[best_index]
        tgt = best_term.copy()
        for j in range(n_qubits):
            if j != best_index and tgt[j] and not src[j]:
                gates.append({"name": "CNOT", "ctrl": j, "target": best_index})
                current_basis[best_index] ^= current_basis[j]

        # Now current_basis[best_index] == best_term
        phase = term_to_phase.pop(LinearFunction.to_string(best_term)) % 8
        if phase != 0:
            append_phase(gates, phase, best_index)

    return gates

import numpy as np

def reduce_to_diagonal(matrix: np.ndarray, allow_swap: bool = True, verbose: bool = False) -> list[dict]:
    mat = matrix.copy()
    n = mat.shape[0]
    ops = []
    
    assert mat.shape[0] == mat.shape[1], "Matrix must be square."
    assert np.linalg.matrix_rank(mat) == n, "Matrix must be invertible."
    
    def weight(x):
        return np.count_nonzero(x)

    while True:
        # Check how many rows are already 1-hot
        single_hot = [i for i in range(n) if weight(mat[i]) == 1]
        if len(single_hot) == n:
            break

        # Find best pair: maximize number of ones on denser row after XOR
        best_score = 0
        best_pair = None
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                
                # xor smaller-weight row into larger-weight row
                if weight(mat[i]) < weight(mat[j]):
                    ctrl, target = i, j
                else:
                    ctrl, target = j, i
                
                score = weight(mat[target]) - weight(mat[target] ^ mat[ctrl])
                # We want to reduce the number of ones, so prefer smaller score
                if score > best_score:
                    best_score = score
                    best_pair = (ctrl, target)

        if best_pair is None:
            break  # No further optimization possible

        ctrl, target = best_pair

        mat[target] ^= mat[ctrl]
        ops.append({"name": "CNOT", "ctrl": int(ctrl), "target": int(target)})
        if verbose:
            print(f"Row {target} ^= Row {ctrl} (CNOT)")

    if not is_one_hot_matrix(mat):
        print("Matrix after reduction:")
        print(mat)
        raise RuntimeError("Matrix did not reduce to one-hot form.")


    if allow_swap:
        return ops

    # Force diagonal order using swaps
    for i in range(n):
        row = mat[i]
        one_idx = np.where(row == 1)[0]
        if len(one_idx) != 1:
            raise RuntimeError(f"Row {i} is not 1-hot after reduction.")
        target_col = int(one_idx[0])
        if target_col != i:
            # Swap row i with row target_col using 3 CNOTs
            if verbose:
                print(f"Swapping logical row {i} with {target_col}")
            ops.extend([
                {"name": "CNOT", "ctrl": i, "target": target_col},
                {"name": "CNOT", "ctrl": target_col, "target": i},
                {"name": "CNOT", "ctrl": i, "target": target_col},
            ])
            mat[[i, target_col]] = mat[[target_col, i]]  # keep mat consistent

    return ops

def reverse_cnot_sequence(gates: list[dict]) -> list[dict]:
    reversed_ops = []
    for g in reversed(gates):
        if g["name"] == "CNOT":
            reversed_ops.append(g)  # CNOT is self-inverse
        elif g["name"] == "SWAP":
            i, j = g["ctrl"], g["target"]
            reversed_ops.extend([
                {"name": "CNOT", "ctrl": i, "target": j},
                {"name": "CNOT", "ctrl": j, "target": i},
                {"name": "CNOT", "ctrl": i, "target": j},
            ])
        else:
            raise ValueError(f"Unsupported gate type for reversal: {g}")
    return reversed_ops

def fix_matrix_by_cnot(src: np.ndarray, target: np.ndarray, verbose: bool = True) -> list[dict]:
    assert src.shape == target.shape
    assert np.linalg.matrix_rank(src) == src.shape[0]
    assert np.linalg.matrix_rank(target) == target.shape[0]

    src = src.copy()
    target = target.copy()

    if verbose:
        print("=== Fixing linear transformation ===")
        print("Initial src:")
        print(src)
        print("Target:")
        print(target)

    g_src = reduce_to_diagonal(src, allow_swap=False, verbose=verbose)
    g_target = reduce_to_diagonal(target, allow_swap=False, verbose=verbose)
    g_target_inv = reverse_cnot_sequence(g_target)

    ops = g_src + g_target_inv

    if verbose:
        print("Final composed ops:")
        for op in ops:
            print(op)
    return ops

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
            term_to_phase[term_str] += phase[gate["name"]]
        elif gate["name"] == "CNOT":
            ctrl = gate["ctrl"]
            target = gate["target"]
            if ctrl == target:
                raise ValueError("CNOT gate cannot have the same control and target qubit.")
            lf.apply_cnot(ctrl, target)
        else:
            raise ValueError(f"Unsupported gate: {gate['name']}")

    # Normalize all phase values mod 8 and remove trivial ones
    term_to_phase = {
        k: v % 8 for k, v in term_to_phase.items() if v % 8 != 0
    }

    # Synthesize parity strings and track resulting transformation
    gates_out = []
    _lf = LinearFunction(n_qubits)
    synthesized = synthesize_parity_strings(term_to_phase, n_qubits)

    for g in synthesized:
        gates_out.append(g)
        if g["name"] == "CNOT":
            _lf.apply_cnot(g["ctrl"], g["target"])

    # Fix _lf to match target lf by Gaussian elimination over GF(2)
    fix_gates = fix_matrix_by_cnot(_lf.matrix, lf.matrix)
    
    _lf.apply_gates(fix_gates)
    assert np.array_equal(_lf.matrix, lf.matrix), "Fixing failed to match target matrix."
    
    gates_out.extend(fix_gates)

    return gates_out

def main():
    print("=== Test: LinearFunction from CNOT gates ===")
    gates = [
        {"name": "T", "target": 0},
        {"name": "T", "target": 1},
        {"name": "CNOT", "ctrl": 0, "target": 1},
        {"name": "CNOT", "ctrl": 1, "target": 0},
        {"name": "T", "target": 1},
        {"name": "T", "target": 0},
    ]
    n = 2
    new_gates = optimize_cnot_phase_block(gates, n)
    print(new_gates)

if __name__ == "__main__":
    main()
