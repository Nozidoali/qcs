from rich.pretty import pprint
from .common import LogicNetwork, LogicGate, QuantumCircuit

def xor_block_grouping(network: LogicNetwork, verbose: bool = False) -> QuantumCircuit:
    _is_valid = lambda x: network.num_fanouts(x) == 1 or network.is_pi(x)
    qubit_of: dict[str, int] = {pi: i for i, pi in enumerate(network.inputs)}
    n_qubits: int = len(qubit_of)
        
    for node, gate in network.gates.items():
        print(f"Processing node {node}: {gate}")
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
            if c1 is c2:
                if p1 != p2: pass 
                else: circuit.add_cnot(c1, qubit, p1)
            circuit.add_toffoli(c1, c2, qubit, p1, p2, qubit_is_clean[qubit])
        elif gate.is_xor:
            c1, c2 = map(lambda x: qubit_of[x], gate.inputs)
            p1, p2 = gate.data["p1"], gate.data["p2"]
            if c1 is c2: continue
            circuit.add_cnot(c1, c2, p1^p2)
        qubit_is_clean[qubit] = False
    return circuit

def uniquify_cuts(cuts: list[list[str]]) -> list[list[str]]:
    _hash = lambda x: tuple(sorted(x))
    return list({ _hash(cut): cut for cut in cuts }.values())

def merge_cuts(cuts1: list[list[str]], cuts2: list[list[str]]) -> list[list[str]]:
    return [list(set(x[:]) | set(y[:])) for x in cuts1 for y in cuts2]

def filter_cuts(cuts: list[list[str]], max_size: int = 6, max_count: int = 1000) -> list[list[str]]:
    return [cut for cut in uniquify_cuts(cuts) if len(cut) <= max_size][:max_count]

def enumerate_cuts(network: LogicNetwork, use_unary_and: bool = False) -> dict[str, list]:
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
            node_to_cuts[node].extend(merge_cuts(node_to_cuts[gate.inputs[0]], node_to_cuts[gate.inputs[1]]))
        else: raise ValueError(f"Unsupported number of inputs: {n_inputs}")
        node_to_cuts[node] = filter_cuts(node_to_cuts[node])
    return node_to_cuts

def extract_subnetwork(network: LogicNetwork, root: str, cut: list[str]) -> LogicNetwork:
    sub_network = LogicNetwork()
    for node in cut: sub_network.create_pi(node)
    def extract_subnetwork_rec(_n: str) -> None:
        if sub_network.has(_n): return
        assert network.is_gate(_n)
        for f in network.fanins(_n): extract_subnetwork_rec(f)
        sub_network.clone_gate(network.get_gate(_n))
    extract_subnetwork_rec(root)
    sub_network.create_po(root)
    sub_network._compute_fanouts()
    return sub_network

def eval_network(network: LogicNetwork) -> dict[str, int]:
    circuit = xor_block_grouping(network, verbose=False)
    return {"n_q": circuit.n_qubits, "n_t": circuit.num_t, "num_ands": network.num_ands}

def _retrieve_nework_rec(network: LogicNetwork, circuit: QuantumCircuit, node_to_cut: dict[str, list], node_to_qubit: dict[str, int], node: str) -> None:
    if node in node_to_qubit: return node_to_qubit[node]
    assert node in node_to_cut, f"Node {node} not found in cuts"
    cut: list[str] = node_to_cut[node]
    root_index: int = circuit.request_qubit()
    for i, f in enumerate(cut):
        _retrieve_nework_rec(network, circuit, node_to_cut, node_to_qubit, f)
    gates_to_add: list[LogicGate] = [network.gates[x] for x in network.collect_nodes_in_topological_order(node, cut)]
    gate: LogicGate
    for i, gate in enumerate(gates_to_add):
        if gate.is_buf: continue
        elif gate.is_xor:
            for f in gate.inputs:
                if node_to_qubit[f] != root_index:
                    circuit.add_cnot(node_to_qubit[f], root_index)
        elif gate.is_and:
            # TODO: consider the polarity of the gate
            if node_to_qubit[gate.inputs[0]] == node_to_qubit[gate.inputs[1]]:
                if gate.data["p1"] != gate.data["p2"]:
                    circuit.add_cnot(node_to_qubit[gate.inputs[0]], root_index)
                continue
            circuit.add_toffoli(node_to_qubit[gate.inputs[0]], node_to_qubit[gate.inputs[1]], root_index, clean=(i==0))
        node_to_qubit[gate.output] = root_index

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

def area_oriented_mapping(network: LogicNetwork, node_to_cuts: dict[str, list]) -> dict[str, list]:
    node_to_cost: dict[str, dict] = {}
    for pi in network.inputs:
        node_to_cost[pi] = {"cut": [pi], "t_cost": 0, "n_cost": 0, "qubits": set([pi])}
    for root, cuts in node_to_cuts.items():
        best_cut, best_t_cost, best_n_cost, best_qubits = None, float("inf"), float("inf"), set()
        for cut in cuts:
            if not all([node in node_to_cost for node in cut]): continue
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

def extract(network: LogicNetwork) -> QuantumCircuit:
    node_to_cuts: dict[str, list] = enumerate_cuts(network)
    node_to_cut:  dict[str, list] = area_oriented_mapping(network, node_to_cuts)
    circuit: QuantumCircuit = retrieve_network(network, node_to_cut)
    return circuit
