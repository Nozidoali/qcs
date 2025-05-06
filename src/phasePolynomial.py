import itertools
import gurobipy as gp
import numpy as np
from gurobipy import GRB

def generate_xor_truth_tables(n_qubits: int):
    truth_tables = set()
    for config in itertools.product([0, 1, 2], repeat=n_qubits):
        table = []
        for x in range(2**n_qubits):
            result = 0
            for i in range(n_qubits):
                bit = (x >> i) & 1
                if config[i] == 1: result ^= bit
                elif config[i] == 2: result ^= 1 ^ bit
            table.append(result)
        truth_tables.add((tuple(table), tuple(config)))
    return list(truth_tables)

def synthesize_tt(tt: str, verbose: bool = False) -> list[float]:
    tt = tt.replace("_", "")
    n_qubits: int = int(np.log2(len(tt)))
    A = generate_xor_truth_tables(n_qubits)
    n_vars: int = len(A)
    n_patterns: int = len(tt)
    if verbose:
        print("Coefficient Matrix:")
        for i in range(n_vars):
            _tt, _config = A[i]
            print(f"tt: {_tt}, config: {_config}")
    model = gp.Model("Phase Polynomial Synthesis")
    X_UB: int = 7
    X_LB: int = 0
    Q_LB: int = int(np.floor(X_LB / 2))
    Q_UB: int = int(np.floor(X_UB / 2))
    x = model.addVars(n_vars, vtype=GRB.INTEGER, name="x", lb=X_LB, ub=X_UB)
    q = model.addVars(n_vars, vtype=GRB.INTEGER, name="q", lb=Q_LB, ub=Q_UB)
    d = model.addVars(n_vars, vtype=GRB.BINARY, name="d")
    for i in range(n_vars):
        model.addConstr(x[i] == 2 * q[i] + d[i], name=f"mod2_{i}")
    model.setObjective(gp.quicksum(d[i] for i in range(n_vars)), GRB.MINIMIZE)

    vq = model.addVars(n_patterns, vtype=GRB.INTEGER, name="vq")
    for j in range(n_patterns):
        if tt[j] not in ["0", "1"]:
            continue  # don't care
        model.addConstr(
            gp.quicksum(A[k][0][j] * x[k] for k in range(n_vars))
            == vq[j] * 8 + int(tt[j]) * 4,
            name=f"phase_{j}",
        )
    model.update()
    model.optimize()
    model.write("model.lp")
    if model.status == GRB.OPTIMAL:
        solution = model.getAttr("x", x)
        print("Optimal solution:")
        for i in range(n_vars):
            print(f"x[{i}] = {solution[i]}")
    else:
        print("No optimal solution found.")
        return None
    return [solution[i] for i in range(n_vars)]
