from rich.pretty import pprint

from logicNetwork import LogicNetwork
from quantumCircuit import QuantumCircuit
from cutEnumeration import enumerate_cuts, area_oriented_mapping
from visualization import plot_network, plot_circuit

def _retrieve_nework_rec(network: LogicNetwork, circuit: QuantumCircuit, node_to_cut: dict[str, list], node_to_qubit: dict[str, int], node: str) -> int:
    if node in node_to_qubit: return node_to_qubit[node]
    assert node in node_to_cut, f"Node {node} not found in cuts"
    pass

def retrieve_network(network: LogicNetwork, node_to_cut: dict[str, list]) -> QuantumCircuit:
    circuit: QuantumCircuit = QuantumCircuit()
    node_to_qubit: dict[str, int] = {}
    
    for i, pi in enumerate(network.inputs):
        node_to_qubit[pi] = i
        circuit.request_qubit()
        
    for i, po in enumerate(network.outputs):
        po_index: int = _retrieve_nework_rec(network, circuit, node_to_cut, node_to_qubit, po)
        pprint(f"PO: {po} -> {po_index}")

if __name__ == "__main__":
    import os
    from rich.pretty import pprint
    
    benchmark: str = "gf_mult2"
    
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    verilog_file = os.path.join(curr_dir, f"../data/input/{benchmark}.v")
    network = LogicNetwork.from_verilog(open(verilog_file).read())
    plot_network(network, file_name=f"{benchmark}.png")
    node_to_cuts: dict[str, list] = enumerate_cuts(network)
    pprint(node_to_cuts)
    node_to_cut: dict[str, list] = area_oriented_mapping(network, node_to_cuts)
    pprint(node_to_cut)
    
    circuit: QuantumCircuit = retrieve_network(network, node_to_cut)