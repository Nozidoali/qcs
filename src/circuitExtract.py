import json
from rich.pretty import pprint

from logicNetwork import LogicNetwork, LogicGate
from quantumCircuit import QuantumCircuit
from visualization import plot_circuit, plot_network


def post_process(circuit: QuantumCircuit, **kwargs) -> QuantumCircuit:
    run_zx: bool = kwargs.get("run_zx", False)
    verbose: bool = kwargs.get("verbose", False)

    qasm_str: str = circuit.to_qasm(run_zx = run_zx)
    if verbose: pprint(qasm_str.splitlines())
    circuit_opt = QuantumCircuit.from_qasm(qasm_str)
    
    circuit_new = QuantumCircuit()
    circuit_new.request_qubits(circuit_opt.n_qubits)
    is_had: dict[int, bool] = {i: False for i in range(circuit_opt.n_qubits)}
    for i, gate in enumerate(circuit_opt.gates):
        if gate["name"] == "HAD":
            is_had[gate["target"]] = not is_had[gate["target"]]
        else:
            for j in QuantumCircuit.deps_of(gate):
                if is_had[j]:
                    circuit_new.add_gate({"name": "HAD", "target": j})
                    is_had[j] = False
            circuit_new.add_gate(gate)
    for j in range(circuit_opt.n_qubits):
        if is_had[j]:
            circuit_new.add_gate({"name": "HAD", "target": j})
            is_had[j] = False
    return circuit_new

def xor_block_grouping(network: LogicNetwork, **kwargs) -> QuantumCircuit:
    plot_network_v: bool = kwargs.get("plot_network", False)
    plot_circuit_v: bool = kwargs.get("plot_circuit", False)
    verbose: bool = kwargs.get("verbose", False)

    _is_valid = lambda x: network.num_fanouts(x) == 1 or network.is_pi(x)

    qubit_of: dict[str, int] = {pi: i for i, pi in enumerate(network.inputs)}
    n_qubits: int = len(qubit_of)
        
    for node, gate in network.gates.items():
        if gate.is_and:
            qubit_of[node] = n_qubits
            n_qubits += 1
        elif gate.is_xor:
            valid_fanins: list[str] = [f for f in gate.inputs if _is_valid(f)]
            if len(valid_fanins) == 0:
                qubit_of[node] = n_qubits
                n_qubits += 1
            else:
                for f in valid_fanins: qubit_of[f] = qubit_of[valid_fanins[0]]
                qubit_of[node] = qubit_of[valid_fanins[0]]
        elif gate.is_buf: qubit_of[node] = qubit_of[gate.inputs[0]]
        else: raise ValueError(f"Unknown gate type: {gate}")
    
    old_to_new: dict[int, int] = {}
    for node, qubit in qubit_of.items():
        if qubit not in old_to_new: old_to_new[qubit] = len(old_to_new)
        qubit_of[node] = old_to_new[qubit]
    n_qubits = len(old_to_new)
    
    if verbose: pprint(qubit_of)
    
    circuit = QuantumCircuit()
    circuit.request_qubits(n_qubits)
    qubit_is_clean: dict[int, bool] = {i: True for i in range(n_qubits)}
    
    for node, gate in network.gates.items():
        qubit: int = qubit_of[node]
        if gate.is_and:
            c1, c2 = map(lambda x: qubit_of[x], gate.inputs)
            p1, p2 = gate.data["p1"], gate.data["p2"]
            circuit.add_toffoli(c1, c2, qubit, p1, p2, qubit_is_clean[qubit])
        elif gate.is_xor:
            c1, c2 = map(lambda x: qubit_of[x], gate.inputs)
            p1, p2 = gate.data["p1"], gate.data["p2"]
            if c1 is c2: continue
            circuit.add_cnot(c1, c2, p1^p2)
        qubit_is_clean[qubit] = False
    circuit = post_process(circuit, **kwargs)
    if plot_network_v: plot_network(network, show_name=verbose)
    if plot_circuit_v: plot_circuit(circuit)
    return circuit


def _uniquify_cuts(cuts: list[list[str]]) -> list[list[str]]:
    _hash = lambda x: tuple(sorted(x))
    return list({ _hash(cut): cut for cut in cuts }.values())

def _merge_cuts(cuts1: list[list[str]], cuts2: list[list[str]]) -> list[list[str]]:
    return [list(set(x[:]) | set(y[:])) for x in cuts1 for y in cuts2]

def _filter_cuts(cuts: list[list[str]], **kwargs) -> list[list[str]]:
    _MAX_INT: int = 2**31 - 1
    max_cut_size: int = kwargs.get("max_cut_size", _MAX_INT)
    max_cut_count: int = kwargs.get("max_cut_count", _MAX_INT)
    return [cut for cut in _uniquify_cuts(cuts) if len(cut) <= max_cut_size][:max_cut_count]

def enumerate_cuts(network: LogicNetwork, **kwargs) -> dict[str, list]:
    use_unary_and: bool = kwargs.get("use_unary_and", False)
    node_to_cuts: dict[str, list[list[str]]] = {pi: [[pi]] for pi in network.inputs}
    for node, gate in network.gates.items():
        node_to_cuts[node] = [[node], gate.inputs[:]]
        assert all(f in node_to_cuts or network.is_pi(f) for f in gate.inputs)
        n_inputs = len(gate.inputs)
        if not use_unary_and and gate.is_and:
            node_to_cuts[node] = [[gate.inputs[0], gate.inputs[1]]]
            continue
        if n_inputs == 1: node_to_cuts[node].extend(node_to_cuts[gate.inputs[0]])
        elif n_inputs == 2: 
            node_to_cuts[node].extend(_merge_cuts(node_to_cuts[gate.inputs[0]], node_to_cuts[gate.inputs[1]]))
        else: raise ValueError(f"Unsupported number of inputs: {n_inputs}")
        node_to_cuts[node] = _filter_cuts(node_to_cuts[node], **kwargs)
    return node_to_cuts

def extract_subnetwork(network: LogicNetwork, root: str, cut: list[str]) -> LogicNetwork:
    sub_network = LogicNetwork()
    for node in cut: sub_network.create_pi(node)
    def extract_rec(_n: str) -> None:
        if sub_network.has(_n): return
        assert network.is_gate(_n)
        for f in network.fanins(_n): extract_rec(f)
        sub_network.clone_gate(network.get_gate(_n))
    extract_rec(root)
    sub_network.create_po(root)
    sub_network._compute_fanouts()
    return sub_network

def eval_network(network: LogicNetwork) -> dict[str, int]:
    circuit = xor_block_grouping(network, verbose=False, run_zx=True)
    return {"n_q": circuit.n_qubits, "n_t": circuit.num_t, "n_ands": network.n_ands}

def area_oriented_mapping(network: LogicNetwork, node_to_cuts: dict[str, list]) -> dict[str, list]:
    node_to_cost: dict[str, dict] = {}
    for pi in network.inputs:
        node_to_cost[pi] = {"cut": [pi], "t_cost": 0, "n_cost": 0, "qubits": set([pi])}
    for root, cuts in node_to_cuts.items():
        best_cut: list = None
        best_t_cost: int = float("inf")
        best_n_cost: int = float("inf")
        best_qubits: set = set()
        for cut in cuts:
            is_valid: bool = all([node in node_to_cost for node in cut])
            if not is_valid: continue
            subnetwork = extract_subnetwork(network, root, cut)
            _t_cost: float = eval_network(subnetwork)["n_t"]
            _qubits: set = set([root])
            for i in range(len(cut)):
                _t_cost += node_to_cost[cut[i]]["t_cost"]
                _qubits = _qubits.union(_qubits, node_to_cost[cut[i]]["qubits"])
            # if _t_cost > best_t_cost: continue
            # if _t_cost == best_t_cost and len(_qubits) > best_n_cost: continue
            if len(_qubits) > best_n_cost: continue
            if len(_qubits) == best_n_cost and _t_cost > best_t_cost: continue
            best_cut, best_n_cost, best_t_cost, best_qubits = cut[:], len(_qubits), _t_cost, _qubits
        node_to_cost[root] = {"cut": best_cut, "t_cost": best_t_cost, "n_cost": best_n_cost, "qubits": best_qubits}
    return {node: node_to_cost[node]["cut"] for node in node_to_cost}

def _collect_nodes_in_topological_order(network: LogicNetwork, root: str, cut: list[str]) -> list[str]:
    visited: set[str] = set()
    order: list[str] = []
    def _post_order_rec(node: str) -> None:
        if node in visited: return
        if node in cut: return
        for f in network.fanins(node):
            _post_order_rec(f)
        visited.add(node)
        order.append(node)
    _post_order_rec(root)
    return order[:]

def _retrieve_nework_rec(network: LogicNetwork, circuit: QuantumCircuit, node_to_cut: dict[str, list], node_to_qubit: dict[str, int], node: str) -> None:
    if node in node_to_qubit: return node_to_qubit[node]
    assert node in node_to_cut, f"Node {node} not found in cuts"
    cut: list[str] = node_to_cut[node]
    root_index: int = circuit.request_qubit()
    for i, f in enumerate(cut):
        _retrieve_nework_rec(network, circuit, node_to_cut, node_to_qubit, f)
    gates_to_add: list[LogicGate] = [network.gates[x] for x in _collect_nodes_in_topological_order(network, node, cut)]
    gate: LogicGate
    is_clean: bool = True
    for gate in gates_to_add:
        if gate.is_buf: continue
        elif gate.is_xor:
            for f in gate.inputs:
                if node_to_qubit[f] != root_index:
                    circuit.add_cnot(node_to_qubit[f], root_index)
        elif gate.is_and:
            circuit.add_toffoli(node_to_qubit[gate.inputs[0]], node_to_qubit[gate.inputs[1]], root_index, clean=is_clean)
        node_to_qubit[gate.output] = root_index
        is_clean = False

def retrieve_network(network: LogicNetwork, node_to_cut: dict[str, list]) -> QuantumCircuit:
    circuit: QuantumCircuit = QuantumCircuit()
    node_to_qubit: dict[str, int] = {}
    for pi in network.inputs:
        node_to_qubit[pi] = circuit.request_qubit()
    for po in network.outputs:
        _retrieve_nework_rec(network, circuit, node_to_cut, node_to_qubit, po)
    return circuit

def extract_simple(network: LogicNetwork) -> QuantumCircuit:
    circuit = QuantumCircuit()
    qubits = {}
    for _, input in enumerate(network.inputs):
        qubits[input] = circuit.request_qubit()
    for node, gate in network.gates.items():
        target = qubits[node] = circuit.request_qubit()
        if gate.is_and:
            ctrl1, ctrl2 = map(lambda x: qubits[x], gate.inputs)
            p1, p2 = gate.data["p1"], gate.data["p2"]
            circuit.add_toffoli(ctrl1, ctrl2, target, p1, p2, True)
        else:
            ctrl = qubits[gate.inputs[0]]
            circuit.add_cnot(ctrl, target)
    return circuit

def extract_q_opt(network: LogicNetwork) -> QuantumCircuit:
    node_to_cuts: dict[str, list] = enumerate_cuts(network)
    node_to_cut:  dict[str, list] = area_oriented_mapping(network, node_to_cuts)
    circuit: QuantumCircuit = retrieve_network(network, node_to_cut)
    return post_process(circuit, run_zx=True)