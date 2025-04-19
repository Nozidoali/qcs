from quantumCircuit import QuantumCircuit
import matplotlib.pyplot as plt
import matplotlib.transforms as mtrans


def plot_circuit(circuit: QuantumCircuit, **kwargs) -> None:
    f = kwargs.get("factor", 0.2)
    _, ax = plt.subplots(figsize=(len(circuit.gates) * f, circuit.n_qubits * f))
    ax.axis("off")

    y = {q: q for q in range(circuit.n_qubits)}
    blend = mtrans.blended_transform_factory(ax.transAxes, ax.transData)

    [ax.axhline(yy, ls=':', lw=1, c='gray') for yy in y.values()]
    [ax.text(0, yy, f"q{q}", ha='right', va='center',
            fontsize=10, transform=blend, clip_on=False)
    for q, yy in y.items()]

    dot   = lambda x, yy, c='b': ax.plot([x], [yy], f'{c}o')
    xmark = lambda x, yy, c='b': ax.plot([x], [yy], f'{c}x')
    vline = lambda x, y1, y2, c='b': ax.plot([x, x], [y1, y2],  c)
    coord = lambda g, k: y[g[k]] 

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
            dot(t, coord(g, "target"), c='r')
        elif n in {"X", "S", "H"}:
            dot(t, coord(g, "target"), c='y')

    plt.tight_layout(pad=0.5)
    plt.savefig("circuit.png")