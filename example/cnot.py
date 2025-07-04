from qcs import LinearFunction, reduce_to_diagonal, is_diagonal_matrix, is_one_hot_matrix
import numpy as np
import tqdm

def test_random_matrix():
    n: int = 10
    m: int = 10
    for _ in tqdm.tqdm(range(100)):
        lf = LinearFunction(n)
        for i in range(m):
            # Randomly choose two qubits to apply CNOT
            q0, q1 = np.random.choice(n, 2, replace=False)
            lf.apply_cnot(q0, q1)
        mat = lf.matrix.copy()
        gates = reduce_to_diagonal(mat, allow_swap=True)
        lf2 = LinearFunction(n)
        lf2.matrix = mat.copy()
        lf2.apply_gates(gates)
        if not is_one_hot_matrix(lf2.matrix):
            # print lf.matrix
            print(lf2.matrix)
            assert False, "Matrix should reduce to diagonal form."

if __name__ == "__main__":
    test_random_matrix()
    print("All tests passed!")