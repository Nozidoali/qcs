from rich.pretty import pprint

from logicNetwork import LogicNetwork, LogicGate
from quantumCircuit import QuantumCircuit
from cutEnumeration import enumerate_cuts, area_oriented_mapping
from visualization import plot_network, plot_circuit

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

    # TODO: map the logic
    gates_to_add: list[LogicGate] = [network.gates[x] for x in _collect_nodes_in_topological_order(network, node, cut)]
    
    gate: LogicGate
    for gate in gates_to_add:
        if gate.is_buf: continue
        if gate.is_xor: continue
        if gate.is_and:
            circuit.add_toffoli(node_to_qubit[gate.inputs[0]], node_to_qubit[gate.inputs[1]], root_index)

def retrieve_network(network: LogicNetwork, node_to_cut: dict[str, list]) -> QuantumCircuit:
    circuit: QuantumCircuit = QuantumCircuit()
    node_to_qubit: dict[str, int] = {}
    
    for pi in network.inputs:
        node_to_qubit[pi] = circuit.request_qubit()
        
    for po in network.outputs:
        _retrieve_nework_rec(network, circuit, node_to_cut, node_to_qubit, po)
    return circuit

if __name__ == "__main__":
    import os
    from rich.pretty import pprint
    
    benchmark: str = "gf_mult2"
    
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    verilog_file = os.path.join(curr_dir, f"../data/input/{benchmark}.v")
    network = LogicNetwork.from_verilog(open(verilog_file).read())
    plot_network(network, file_name=f"{benchmark}_network.png")
    node_to_cuts: dict[str, list] = enumerate_cuts(network)
    pprint(node_to_cuts)
    node_to_cut: dict[str, list] = area_oriented_mapping(network, node_to_cuts)
    pprint(node_to_cut)
    
    circuit: QuantumCircuit = retrieve_network(network, node_to_cut)
    plot_circuit(circuit, file_name=f"{benchmark}_circuit.png")