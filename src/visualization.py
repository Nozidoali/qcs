from quantumCircuit import QuantumCircuit
from logicNetwork import LogicNetwork
import matplotlib.pyplot as plt
import matplotlib.transforms as mtrans
import pygraphviz as pgv

def plot_network(network: LogicNetwork, **kwargs) -> None:
    show_name: bool = kwargs.get("show_name", True)
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
    graph.draw("network.png")

def plot_circuit(circuit: QuantumCircuit, **kwargs) -> None:
    f = kwargs.get("factor", 0.2)
    _, ax = plt.subplots(figsize=(len(circuit.gates) * f, circuit.n_qubits * f))
    ax.axis("off")

    y = {q: q for q in range(circuit.n_qubits)}
    blend = mtrans.blended_transform_factory(ax.transAxes, ax.transData)

    [ax.axhline(yy, ls=':', lw=1, c='gray') for yy in y.values()]
    [ax.text(0, yy, f"q{q}", ha='right', va='center', fontsize=10, transform=blend, clip_on=False) for q, yy in y.items()]

    dot    = lambda x, yy, c='b'    : ax.plot([x], [yy], f'{c}o')
    square = lambda x, yy, c='b'    : ax.plot([x], [yy], f'{c}s', ms=10)
    xmark  = lambda x, yy, c='b'    : ax.plot([x], [yy], f'{c}x')
    vline  = lambda x, y1, y2, c='b': ax.plot([x, x], [y1, y2],  c)
    text   = lambda x, y, s, c='b'  : ax.text(x, y, s, ha='center', va='center', fontsize=10, color=c)
    coord  = lambda g, k: y[g[k]] 

    for t, g in enumerate(circuit.gates):
        n = g["name"]
        if n == "CNOT":
            vline(t, coord(g, "ctrl"), coord(g, "target"))
            dot  (t, coord(g, "ctrl"))
            xmark(t, coord(g, "target"))
        elif n == "Tof":
            for c in ("ctrl1", "ctrl2"):
                vline(t, coord(g, c), coord(g, "target"))
                dot(t,   coord(g, c))
            xmark(t, coord(g, "target"))
        elif n in {"T", "Tdg"}:
            square(t, coord(g, "target"), c='r')
            l = {"T": "T", "Tdg": "T-"}[n]
            text(t, coord(g, "target"), l, c='white')
        elif n in {"X", "S", "HAD"}:
            square(t, coord(g, "target"), c="y")
            l = {"X": "X", "S": "S", "HAD": "H"}[n]
            text(t, coord(g, "target"), l, c='white')

    plt.tight_layout(pad=0.5)
    plt.savefig("circuit.png")