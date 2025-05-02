from rich.pretty import pprint

from logicNetwork import LogicNetwork
from quantumCircuit import QuantumCircuit
from cutEnumeration import enumerate_cuts, extract_subnetwork
from circuitExtract import xor_block_grouping
from visualization import plot_circuit, plot_network

idx = 0

def eval_network(network: LogicNetwork) -> dict[str, int]:
    circuit = xor_block_grouping(network, verbose=False, run_zx=True)
    return {"n_q": circuit.n_qubits, "n_t": circuit.num_t, "n_ands": network.n_ands}

def retrieve_network(network: LogicNetwork, cuts: dict[list]) -> QuantumCircuit:
    pass

if __name__ == "__main__":
    import os
    from rich.pretty import pprint
    
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    verilog_file = os.path.join(curr_dir, "../data/input/gf_mult4.v")
    network = LogicNetwork.from_verilog(open(verilog_file).read())
    plot_network(network, file_name="gf_mult4.png")
    
    node_to_cuts = enumerate_cuts(network)

    # root = "po1"
    # cut = ["pi4", "pi2", "pi3", "new_new_n8"]
    # subnetwork = extract_subnetwork(network, root, cut)
    # eval_results = eval_network(subnetwork)

    eval_results = {}
    node_to_cost: dict[str, dict] = {}
    for pi in network.inputs:
        node_to_cost[pi] = {"cut": [pi], "t_cost": 0, "n_cost": 0}
    for root, cuts in node_to_cuts.items():
        eval_results[root] = []
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
    pprint(node_to_cost)