from logicNetwork import LogicNetwork
from circuitExtract import xor_block_grouping

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
        node_to_cost[pi] = {"cut": [pi], "t_cost": 0, "n_cost": 0}
    for root, cuts in node_to_cuts.items():
        best_cut: list = None
        best_t_cost: int = float("inf")
        best_n_cost: int = float("inf")
        for cut in cuts:
            is_valid: bool = all([node in node_to_cost for node in cut])
            if not is_valid: continue
            subnetwork = extract_subnetwork(network, root, cut)
            _t_cost: float = eval_network(subnetwork)["n_t"]
            _n_cost: float = eval_network(subnetwork)["n_q"]
            for i in range(len(cut)):
                _t_cost += node_to_cost[cut[i]]["t_cost"]
                _n_cost += node_to_cost[cut[i]]["n_cost"]
            if _t_cost > best_t_cost: continue
            if _t_cost == best_t_cost and _n_cost > best_n_cost: continue
            best_cut, best_n_cost, best_t_cost = cut[:], _n_cost, _t_cost
        node_to_cost[root] = {"cut": best_cut, "t_cost": best_t_cost, "n_cost": best_n_cost}
    return {node: node_to_cost[node]["cut"] for node in node_to_cost}

if __name__ == "__main__":
    import os
    from rich.pretty import pprint
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    verilog_file = os.path.join(curr_dir, "../data/input/gf_mult2.v")
    network = LogicNetwork.from_verilog(open(verilog_file).read())
    cuts = enumerate_cuts(network)
    pprint(cuts)
    subnetwork = extract_subnetwork(network, "po0", ["pi1", "pi2", "pi3", "pi4"])
