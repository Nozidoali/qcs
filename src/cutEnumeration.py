from logicNetwork import LogicNetwork

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
    node_to_cuts: dict[str, list[list[str]]] = {pi: [[pi]] for pi in network.inputs}
    for node, gate in network.gates.items():
        node_to_cuts[node] = [[node], gate.inputs[:]]
        assert all(f in node_to_cuts or network.is_pi(f) for f in gate.inputs)
        n_inputs = len(gate.inputs)
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
        for f in network.fanins(_n):
            extract_rec(f)
        sub_network.clone_gate(network.get_gate(_n))
    extract_rec(root)
    sub_network.create_po(root)
    sub_network._compute_fanouts()
    return sub_network

if __name__ == "__main__":
    import os
    from rich.pretty import pprint
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    verilog_file = os.path.join(curr_dir, "../data/input/gf_mult2.v")
    network = LogicNetwork.from_verilog(open(verilog_file).read())
    cuts = enumerate_cuts(network)
    pprint(cuts)
    subnetwork = extract_subnetwork(network, "po0", ["pi1", "pi2", "pi3", "pi4"])
