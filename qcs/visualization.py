import matplotlib.pyplot as plt
import matplotlib.transforms as mtrans

from .common import QuantumCircuit, LogicNetwork

def plot_network(network: LogicNetwork, **kwargs) -> None:
    import pygraphviz as pgv
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


def plot_circuit(circ, fn=None):
    xc, yc, xm, ym = .4, .5, .25, .25
    ms = 16
    colors = {"CNOT":"b","Tof":"g","T":"r","Tdg":"r","X":"b","S":"m","HAD":"g"}
    
    gloc = schedule_gates(circ)
    cols = max(gloc.values()) + 1 if gloc else 1
    x = {i: c * xc for i, c in gloc.items()}
    y = {q: (circ.n_qubits - 1 - q) * yc for q in range(circ.n_qubits)}
    
    w, h = cols * xc + 2 * xm, (circ.n_qubits-1) * yc + 2 * ym
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(-xm, cols * xc + xm), ax.set_ylim(-ym, (circ.n_qubits-1) * yc + ym), ax.axis("off")
    
    tr = mtrans.blended_transform_factory(ax.transAxes, ax.transData)
    [ax.axhline(v, lw=1, c="gray") for v in y.values()]
    [ax.text(-.02, v, f"q{k}", ha="right", va="center", transform=tr, fontsize=8) for k, v in y.items()]
    
    dot    = lambda p, q, c='b': ax.plot([p], [q], f'{c}o')
    square = lambda p, q, c='b': ax.plot([p], [q], f'{c}s', ms=ms)
    xmark  = lambda p, q, c='b': ax.plot([p], [q], f'{c}x')
    vline  = lambda p, q1, q2, c='b': ax.plot([p, p], [q1, q2], c)
    text   = lambda p, q, s, c='k': ax.text(p, q, s, ha="center", va="center", fontsize=10, color=c)
    
    for i, g in enumerate(circ.gates):
        p, n = x[i], g["name"]
        if n == "CNOT":
            vline(p, y[g["ctrl"]], y[g["target"]])
            dot(p, y[g["ctrl"]])
            xmark(p, y[g["target"]])
        elif n == "CZ":
            vline(p, y[g["ctrl"]], y[g["target"]])
            dot(p, y[g["ctrl"]])
            dot(p, y[g["target"]])
        elif n == "Tof":
            tgt = y[g["target"]]
            for c in ("ctrl1", "ctrl2"): vline(p, y[g[c]], tgt); dot(p, y[g[c]])
            xmark(p, tgt)
        elif n in {"T", "Tdg"}:
            qt = y[g["target"]]; square(p, qt, colors[n]); text(p, qt, "T" if n == "T" else "T", "white")
        elif n in {"X", "S", "HAD"}:
            qt = y[g["target"]]; square(p, qt, colors[n]); text(p, qt, {"X":"X","S":"S","HAD":"H"}[n], "white")
        else:
            qt = y.get(g.get("target", 0), 0); square(p, qt, 'k'); text(p, qt, n, 'white')
            
    (plt.savefig(fn, bbox_inches="tight") if fn else plt.show()) and plt.close(fig)