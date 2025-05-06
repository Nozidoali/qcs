from rich.pretty import pprint

from logicNetwork import LogicNetwork
from quantumCircuit import QuantumCircuit
from cutEnumeration import enumerate_cuts, area_oriented_mapping
from visualization import plot_network

def retrieve_network(network: LogicNetwork, node_to_cut: dict[str, list]) -> QuantumCircuit:
    pass

if __name__ == "__main__":
    import os
    from rich.pretty import pprint
    
    benchmark: str = "gf_mult4"
    
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    verilog_file = os.path.join(curr_dir, f"../data/input/{benchmark}.v")
    network = LogicNetwork.from_verilog(open(verilog_file).read())
    plot_network(network, file_name=f"{benchmark}.png")
    node_to_cuts: dict[str, list] = enumerate_cuts(network)
    pprint(node_to_cuts)
    node_to_cut: dict[str, list] = area_oriented_mapping(network, node_to_cuts)
    pprint(node_to_cut)