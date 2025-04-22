import json
from rich.pretty import pprint

from logicNetwork import LogicNetwork
from quantumCircuit import QuantumCircuit
from visualization import plot_circuit, plot_network

AND_GATE_T_COST: int = 4

class Structure:
    def __init__(self, leaves: list[str], root: str, Tcost: int, 
                exposed_signals: list[str] = [], product_terms: list[str] = []):
        self.leaves = leaves
        self.root = root
        self.Tcost = Tcost
        self.exposed_signals = exposed_signals
        self.product_terms = product_terms

    def to_json(self) -> dict:
        return {
            "leaves": self.leaves,
            "root": self.root,
            "T cost": self.Tcost,
            "exposed signals": self.exposed_signals,
            "product terms": self.product_terms
        }

def cut_enumeration(network: LogicNetwork, **kwargs) -> dict[str, list[Structure]]:
    max_inputs: int = kwargs.get("max_inputs", 2)
    
    _is_valid = lambda x: (not network.is_pi(x)) and network.get_gate(x).is_and and network.num_fanouts(x) == 1
    inputs_of = lambda x: network.get_gate(x).inputs
    
    node_to_structures: dict = {}
    for pi in network.inputs:
        node_to_structures[pi] = [Structure([pi], 0, pi)]
    for node, gate in network.gates.items():
        _leaves: set[str] = set(gate.inputs[:])
        if gate.is_and: # AND gate cannot be used in XOR block
            node_to_structures[node] = [Structure(list(_leaves), node, AND_GATE_T_COST, [], [inputs_of(node)[:]])]
            continue
        exposed_signals: set[str] = set({node})
        while True:
            cut_expanded: bool = False
            leaves_added: set[str] = set()
            for l in _leaves:
                _gate = network.get_gate(l)
                if _gate and _gate.is_xor:
                    exposed_signals.add(l)
                    leaves_added.update(inputs_of(l))
                    cut_expanded = True
            _leaves.update(leaves_added)
            _leaves.difference_update(exposed_signals)
            if not cut_expanded: break
        leaf_to_product: dict[str, list[str]] = {_l: [_l] for _l in _leaves}
        for _l in _leaves:
            _product: set[str] = set({_l})
            while len(_product) < max_inputs:
                lits_to_expand: set[str] = {x for x in _product if _is_valid(x)}
                lits_to_add: set[str] = {y for x in lits_to_expand for y in inputs_of(x)}
                if len(lits_to_expand) == 0: break
                _product.update(lits_to_add)
                _product.difference_update(lits_to_expand)
                if len(_product) >= max_inputs: break
            leaf_to_product[_l] = _product
            
        node_to_structures[node] = [Structure(
            list({lit for leaf in _leaves for lit in leaf_to_product[leaf]}),
            node,
            sum((AND_GATE_T_COST * len(leaf_to_product[_l]) for _l in _leaves)),
            list(exposed_signals), 
            [list(leaf_to_product[_l]) for _l in _leaves]
        )]
    return node_to_structures


def library_mapping(network: LogicNetwork, node_to_structures: dict[str, list[Structure]], **kwargs) -> dict[str, Structure]:
    return {k: v[0] for k, v in node_to_structures.items()}


def xor_block_grouping(network: LogicNetwork, **kwargs) -> QuantumCircuit:
    plot_network_v: bool = kwargs.get("plot_network", False)
    plot_circuit_v: bool = kwargs.get("plot_circuit", False)
    verbose: bool = kwargs.get("verbose", False)

    _is_valid = lambda x: (not network.is_pi(x)) and network.num_fanouts(x) == 1

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

    qasm_str: str = circuit.to_qasm(run_zx = True)
    if verbose: pprint(qasm_str.splitlines())
    circuit_opt = QuantumCircuit.from_qasm(circuit.to_qasm(run_zx = True))
    
    if plot_network_v: plot_network(network, show_name=verbose)
    if plot_circuit_v: plot_circuit(circuit_opt)

    return circuit_opt

def xor_block_extraction(network: LogicNetwork, **kwargs) -> QuantumCircuit:
    plot_network_v: bool = kwargs.get("plot_network", True)
    plot_circuit_v: bool = kwargs.get("plot_circuit", True)
    verbose: bool = kwargs.get("verbose", True)

    node_to_structures = cut_enumeration(network, max_inputs=2, **kwargs)
    node_to_best_structure: dict[str, Structure] = library_mapping(network, node_to_structures, **kwargs)
    fanins_of = lambda x: node_to_best_structure[x].leaves

    data = {x: node_to_best_structure[x].to_json() for x, _ in network.gates.items()}
    if verbose: pprint(data)
    
    circuit = QuantumCircuit()
    qubits = {}
    for _, input in enumerate(network.inputs):
        qubits[input] = circuit.request_qubit()
    def _mapping_rec(node: str):
        if node in qubits: return
        for leaf in fanins_of(node):
            _mapping_rec(leaf)
        print(f"Mapping {node} with fanins {fanins_of(node)} and product terms {node_to_best_structure[node].product_terms}")
        qubits[node] = circuit.request_qubit()
        for _p in node_to_best_structure[node].product_terms:
            circuit.add_mcx(
                # TODO: fix the phase
                [qubits[x] for x in _p], qubits[node], [False] * len(_p), False)
    for po in network.outputs: _mapping_rec(po)
    
    if plot_network_v: plot_network(network, show_name=verbose)
    if plot_circuit_v: plot_circuit(circuit)
    return circuit


def extract(network: LogicNetwork) -> QuantumCircuit:
    circuit = QuantumCircuit()
    qubits = {}
    for _, input in enumerate(network.inputs):
        qubits[input] = circuit.request_qubit()
    for node, gate in network.gates.items():
        qubits[node] = circuit.request_qubit()
        if gate.is_and:
            ctrl1 = qubits[gate.inputs[0]]
            ctrl2 = qubits[gate.inputs[1]]
            target = qubits[node]
            p1, p2 = gate.data["p1"], gate.data["p2"]
            circuit.add_toffoli(ctrl1, ctrl2, target, p1, p2, True)
        else:
            ctrl = qubits[gate.inputs[0]]
            target = qubits[gate.output]
            circuit.add_cnot(ctrl, target)
    return circuit