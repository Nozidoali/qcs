from logicNetwork import LogicNetwork, LogicGate
from quantumCircuit import QuantumCircuit
from visualization import plot_circuit

AND_GATE_T_COST: int = 4

class Structure:
    def __init__(self, leaves: list[str], root: str, Tcost: int, 
                exposed_signals: list[str] = [], product_terms: list[str] = []):
        self.leaves = leaves
        self.root = root
        self.Tcost = Tcost
        self.exposed_signals = exposed_signals
        self.product_terms = product_terms


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
            node_to_structures[node] = Structure(list[_leaves], node, AND_GATE_T_COST, [], inputs_of(node))
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
    
        node_to_structures[node] = Structure(
            list({x for _l in _leaves for x in leaf_to_product[_l]}), 
            node,
            sum(AND_GATE_T_COST * len(leaf_to_product[_l]) for _l in _leaves),
            list(exposed_signals), 
            [list(leaf_to_product[_l]) for _l in _leaves]
        )
    return node_to_structures


def xor_block_extraction(network: LogicNetwork, **kwargs) -> QuantumCircuit:
    node_to_structures = cut_enumeration(network, max_inputs=2, **kwargs)
    fanins_of = lambda x: node_to_structures[x].leaves
    
    circuit = QuantumCircuit()
    qubits = {}
    for _, input in enumerate(network.inputs):
        qubits[input] = circuit.request_qubit()

    def _mapping_rec(node: str):
        if node in qubits: return
        for leaf in fanins_of(node):
            _mapping_rec(leaf)
        print(f"Mapping {node} with fanins {fanins_of(node)}")
        qubits[node] = circuit.request_qubit()
        for _p in node_to_structures[node].product_terms:
            circuit.add_mcx(
                # TODO: fix the phase
                [qubits[x] for x in _p], qubits[node], [False] * len(_p), False
            )
    
    for po in network.outputs:
        _mapping_rec(po)
        
    plot_circuit(circuit)
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