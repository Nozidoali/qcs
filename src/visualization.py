from quantumCircuit import QuantumCircuit
from logicNetwork import LogicNetwork
import matplotlib.pyplot as plt
import matplotlib.transforms as mtrans
import pygraphviz as pgv

def plot_network(network: LogicNetwork, **kwargs) -> None:
    show_name: bool = kwargs.get("show_name", True)
    file_name: str = kwargs.get("file_name", "network.png")
    NEW_LINE: str = "\\n"
    graph = pgv.AGraph(directed=True)
    for input in network.inputs:
        graph.add_node(input, shape="box", color="blue")
    for node, gate in network.gates.items():
        label = "&" if gate.is_and else "^" if gate.is_xor else node
        if show_name: label = f"{label}{NEW_LINE}({node})"
        graph.add_node(node, shape="ellipse", color="black", label=label)
        for input in gate.inputs:
            graph.add_edge(input, node)
    graph.layout(prog="dot")
    graph.draw(file_name)
    
def plot_params(circuit: QuantumCircuit, **kwargs) -> dict:
    params: dict = {}
    params["W"] = len(circuit.gates)
    params["H"] = circuit.n_qubits + 2
    params["dpi"] = kwargs.get("dpi", 100)
    params["factor"] = kwargs.get("factor", 0.2)
    params["figsize"] = (params["W"] * params["factor"], params["H"] * params["factor"])
    
    """
        b  blue          m  magenta
        g  green         y  yellow
        r  red           k  black
        c  cyan          w  white
    """
    gate_colors: dict = {
        "CNOT": "b",
        "Tof":  "g",
        "T":    "r",
        "Tdg":  "r",
        "X":    "b",
        "S":    "m",
        "HAD":  "g"
    }
    params["gate_colors"] = gate_colors
    return params
    
def schedule_gates(circuit: QuantumCircuit, **kwargs) -> list:
    remove_overlap: bool = kwargs.get("remove_overlap", True)
    
    gate_loc: dict[int, int] = {}
    level = [-1] * circuit.n_qubits
    for i, gate in enumerate(circuit.gates):
        deps: set[int] = QuantumCircuit.deps_of(gate)
        if remove_overlap:
            min_idx, max_idx = min(deps), max(deps)
            for j in range(min_idx, max_idx + 1):
                deps.add(j)
        max_level: int = 1 + max([level[d] for d in deps])
        for dep in deps: level[dep] = max_level
        gate_loc[i] = max_level
    return gate_loc

def plot_circuit(circuit: QuantumCircuit, **kwargs) -> None:    
    params: dict = plot_params(circuit, **kwargs)
    file_name: str = kwargs.get("file_name", "circuit.png")
    
    _, ax = plt.subplots(figsize=params["figsize"], dpi=params["dpi"])
    ax.axis("off")

    y = {q: q+1 for q in range(circuit.n_qubits)}
    blend = mtrans.blended_transform_factory(ax.transAxes, ax.transData)

    [ax.axhline(yy, ls='-', lw=1, c='gray') for yy in y.values()]
    [ax.text(0, yy, f"q{q}", ha='right', va='center', fontsize=10, transform=blend, clip_on=False) for q, yy in y.items()]
    
    x_of = schedule_gates(circuit)

    dot    = lambda x, yy, c='b'    : ax.plot([x], [yy], f'{c}o')
    square = lambda x, yy, c='b'    : ax.plot([x], [yy], f'{c}s', ms=10)
    xmark  = lambda x, yy, c='b'    : ax.plot([x], [yy], f'{c}x')
    vline  = lambda x, y1, y2, c='b': ax.plot([x, x], [y1, y2],  c)
    text   = lambda x, y, s, c='b'  : ax.text(x, y, s, ha='center', va='center', fontsize=10, color=c)
    coord  = lambda g, k: y[g[k]] 

    for i, g in enumerate(circuit.gates):
        t = x_of[i]
        n = g["name"]
        if n == "CNOT":
            vline(t, coord(g, "ctrl"), coord(g, "target"))
            dot  (t, coord(g, "ctrl"))
            xmark(t, coord(g, "target"))
        elif n == "Tof":
            for c in ("ctrl1", "ctrl2"):
                vline(t, coord(g, c), coord(g, "target"))
                dot  (t, coord(g, c))
            xmark(t, coord(g, "target"))
        elif n in {"T", "Tdg"}:
            square(t, coord(g, "target"), c=params["gate_colors"][n])
            l = {"T": "T", "Tdg": "T-"}[n]
            text(t, coord(g, "target"), l, c='white')
        elif n in {"X", "S", "HAD"}:
            square(t, coord(g, "target"), c=params["gate_colors"][n])
            l = {"X": "X", "S": "S", "HAD": "H"}[n]
            text(t, coord(g, "target"), l, c='white')

    plt.savefig(file_name)
    plt.close()