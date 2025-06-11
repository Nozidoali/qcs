import itertools
import numpy as np
import gurobipy as gp
from gurobipy import GRB
from logicNetwork import LogicNetwork

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

def synthesize_d3(d3: np.ndarray, **kwargs) -> list[float]:
    verbose: bool = kwargs.get("verbose", False)
    timeout: int = kwargs.get("timeout", 10)
    
    n_qubits: int = int(np.log2(d3.size))
    n_patterns: int = d3.size
    
    A = generate_xor_truth_tables(n_qubits)
    n_vars: int = len(A)
    if verbose:
        print("Coefficient Matrix:")
        for i in range(n_vars):
            _tt, _config = A[i]
            print(f"tt: {_tt}, config: {_config}")
    
    gp.setParam("OutputFlag", 0)
    gp.setParam("LogToConsole", 0)
    model = gp.Model("Phase Polynomial Synthesis")
    X_UB: int = 7
    X_LB: int = 0
    Q_LB: int = int(np.floor(X_LB / 2))
    Q_UB: int = int(np.floor(X_UB / 2))
    x = model.addVars(n_vars, vtype=GRB.INTEGER, name="x", lb=X_LB, ub=X_UB)
    q = model.addVars(n_vars, vtype=GRB.INTEGER, name="q", lb=Q_LB, ub=Q_UB)
    d = model.addVars(n_vars, vtype=GRB.BINARY,  name="d")
    for i in range(n_vars):
        model.addConstr(x[i] == 2 * q[i] + d[i], name=f"mod2_{i}")
    model.setObjective(gp.quicksum(d[i] for i in range(n_vars)), GRB.MINIMIZE)

    vq = model.addVars(n_patterns, vtype=GRB.INTEGER, name="vq")
    for j in range(n_patterns):
        if d3[j] < 0:
            continue  # don't care
        model.addConstr(
            gp.quicksum(A[k][0][j] * x[k] for k in range(n_vars))
            == vq[j] * 8 + int(d3[j]),
            name=f"phase_{j}",
        )
    model.update()
    model.setParam("TimeLimit", timeout)
    model.optimize()
    model.write("model.lp")
    if model.status == GRB.OPTIMAL or model.status == GRB.TIME_LIMIT:
        solution = model.getAttr("x", x)
        num_t: float = model.getAttr("ObjVal")
        return num_t, [solution[i] for i in range(n_vars)]
    else: return None

def logic_to_unitary(network: LogicNetwork) -> np.ndarray:
    if network.n_pos != 1: raise NotImplementedError("Only single-output networks are supported.")
    n_qubits: int = network.n_pis + network.n_pos
    unitary: np.ndarray = np.zeros((2**n_qubits, 2**n_qubits), dtype=int)
    network.simulate()
    pattern: int = network.get_pattern(network.outputs[0])
    for _x in range(2**network.n_pis):
        for p in range(2):
            x = (_x << 1) | p
            y = (_x << 1) | (1-p if pattern & (1 << _x) else p)
            unitary[x, y] = 1
    return unitary

def logic_to_d3(network: LogicNetwork) -> np.ndarray:
    if network.n_pos != 1: raise NotImplementedError("Only single-output networks are supported.")
    n_qubits: int = network.n_pis + network.n_pos
    d3: np.ndarray = np.zeros(2**(n_qubits), dtype=int)
    network.simulate()
    pattern: int = network.get_pattern(network.outputs[0])
    for _x in range(2**network.n_pis):
        x = (_x << 1) | 1
        if pattern & (1 << _x): d3[x] = 4
    return d3
