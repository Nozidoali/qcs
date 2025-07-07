import matplotlib.pyplot as plt
import matplotlib.patches as patches

import matplotlib.transforms as mtrans
import numpy as np
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


def plot_truth_table(
    truth_table: list[str],
    n: int,
    m: int,
    filename: str,
    input_names: list[str] = None,
    output_names: list[str] = None
) -> None:
    BOX_SIZE = 0.8
    N = 2 ** n
    assert len(truth_table) == m and all(len(row) == N for row in truth_table)

    input_bits = np.array([[int(b) for b in format(i, f"0{n}b")[::-1]] for i in range(N)]).T
    output_bits = np.array([[int(b) for b in row] for row in truth_table])
    data = np.vstack((input_bits, output_bits))

    if input_names is None:
        input_names = [f"in{i}" for i in range(n)]
    if output_names is None:
        output_names = [f"out{i}" for i in range(m)]

    row_labels = input_names + output_names
    assert len(row_labels) == n + m

    fig, ax = plt.subplots(figsize=(N * 0.4 + 1.5, (n + m) * 0.4))
    ax.set_xlim(-1, N)
    ax.set_ylim(-0.5, n + m - 0.5)
    ax.invert_yaxis()

    for row in range(n + m):
        ax.text(-1, row, row_labels[row], ha='right', va='center', fontsize=10, fontweight='bold')
        for col in range(N):
            val = data[row][col]
            ax.text(col, row, str(val), ha='center', va='center', fontsize=10)
            if row >= n and val == 1:
                rect = patches.Rectangle((col - BOX_SIZE/2, row - BOX_SIZE/2), BOX_SIZE, BOX_SIZE, linewidth=1.2, edgecolor='black', facecolor='none')
                ax.add_patch(rect)

    ax.axhline(y=n - 0.5, color='black', linewidth=1)
    ax.axvline(x=-0.5, color='black', linewidth=1)

    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis('off')
    plt.tight_layout(pad=0.3)
    plt.savefig(filename, dpi=200)
    plt.close()