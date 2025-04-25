from rich.pretty import pprint

from logicNetwork import LogicNetwork
from cutEnumeration import enumerate_cuts, extract_subnetwork
from circuitExtract import xor_block_grouping

def eval_network(network: LogicNetwork) -> dict[str, int]:
    circuit = xor_block_grouping(network)
    return {"n_q": circuit.n_qubits, "n_t": circuit.num_t, "n_ands": network.n_ands}

if __name__ == "__main__":
    import os
    from rich.pretty import pprint
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    verilog_file = os.path.join(curr_dir, "../data/input/gf_mult2.v")
    network = LogicNetwork.from_verilog(open(verilog_file).read())
    node_to_cuts = enumerate_cuts(network)

    eval_results = {}
    for root, cuts in node_to_cuts.items():
        eval_results[root] = []
        for cut in cuts:
            subnetwork = extract_subnetwork(network, root, cut)
            eval_results[root].append({"cut": cut, "eval": eval_network(subnetwork)})
    pprint(eval_results)