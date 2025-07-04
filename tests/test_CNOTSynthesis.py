import numpy as np
from qcs import LinearFunction, reduce_to_diagonal, is_diagonal_matrix, is_one_hot_matrix, fix_matrix_by_cnot

def random_invertible_matrix(n: int, seed=None) -> np.ndarray:
    if seed is not None:
        np.random.seed(seed)
    mat = np.eye(n, dtype=np.uint8)
    lf = LinearFunction(n)
    lf.matrix = mat
    # Apply a few random CNOTs
    for _ in range(n * 3):
        i, j = np.random.choice(n, 2, replace=False)
        lf.apply_cnot(i, j)
    return lf.matrix.copy()


def test_00_identity():
    mat = np.eye(3, dtype=np.uint8)
    gates = reduce_to_diagonal(mat, allow_swap=False)
    lf2 = LinearFunction(3)
    lf2.matrix = mat.copy()
    lf2.apply_gates(gates)
    assert is_diagonal_matrix(lf2.matrix), "Identity should reduce to itself."


def test_01_dense_matrix():
    mat = np.array([
        [1, 1, 1],
        [1, 1, 0],
        [1, 0, 0]
    ], dtype=np.uint8)
    gates = reduce_to_diagonal(mat, allow_swap=True)
    print("Gates:", gates)
    lf2 = LinearFunction(3)
    lf2.matrix = mat.copy()
    lf2.apply_gates(gates)
    assert is_one_hot_matrix(lf2.matrix), "Should reduce to one-hot per row (unordered)."


def test_02_force_diagonal_swap():
    mat = np.array([
        [0, 1, 0],
        [1, 0, 1],
        [1, 1, 0]
    ], dtype=np.uint8)
    gates = reduce_to_diagonal(mat, allow_swap=False)
    lf2 = LinearFunction(3)
    lf2.matrix = mat.copy()
    lf2.apply_gates(gates)
    assert is_diagonal_matrix(lf2.matrix), "Should reduce to identity matrix with swaps."


def test_03_already_one_hot():
    mat = np.array([
        [0, 1, 0],
        [1, 0, 0],
        [0, 0, 1]
    ], dtype=np.uint8)
    gates = reduce_to_diagonal(mat, allow_swap=True)
    lf2 = LinearFunction(3)
    lf2.matrix = mat.copy()
    lf2.apply_gates(gates)
    assert is_one_hot_matrix(lf2.matrix), "One-hot input should stay one-hot."


def test_fix_identity_to_random():
    target = random_invertible_matrix(4, seed=0)
    src = np.eye(4, dtype=np.uint8)
    gates = fix_matrix_by_cnot(src, target, verbose=True)
    lf = LinearFunction(4)
    lf.matrix = src.copy()
    lf.apply_gates(gates)
    assert np.array_equal(lf.matrix, target), "Identity should transform to random invertible."


def test_fix_random_to_random():
    src = random_invertible_matrix(5, seed=1)
    target = random_invertible_matrix(5, seed=2)
    gates = fix_matrix_by_cnot(src, target, verbose=True)
    lf = LinearFunction(5)
    lf.matrix = src.copy()
    lf.apply_gates(gates)
    assert np.array_equal(lf.matrix, target), "Random invertible src should transform to target."


def test_random_matrix():
    n: int = 8
    m: int = 8
    for _ in range(10):
        lf = LinearFunction(n)
        for i in range(m):
            # Randomly choose two qubits to apply CNOT
            q0, q1 = np.random.choice(n, 2, replace=False)
            lf.apply_cnot(q0, q1)
        mat = lf.matrix.copy()
        gates = reduce_to_diagonal(mat, allow_swap=False)
        lf2 = LinearFunction(n)
        lf2.matrix = mat.copy()
        lf2.apply_gates(gates)
        if not is_diagonal_matrix(lf2.matrix):
            # print lf.matrix
            print("Matrix after reduction:", lf.matrix)
        
        assert is_one_hot_matrix(lf2.matrix), "Random matrix should reduce to one-hot matrix."

def main():
    # test_00_identity()
    # print("test_00_identity passed.")

    # test_01_dense_matrix()
    # print("test_01_dense_matrix passed.")

    # test_02_force_diagonal_swap()
    # print("test_02_force_diagonal_swap passed.")

    # test_03_already_one_hot()
    # print("test_03_already_one_hot passed.")

    # test_fix_identity_to_random()
    # print("test_fix_identity_to_random passed.")
    
    # test_fix_random_to_random()
    # print("test_fix_random_to_random passed.")


    test_random_matrix()
    print("All tests passed!")


if __name__ == "__main__":
    main()
