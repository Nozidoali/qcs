from qcs import LogicNetwork, extract

def test_01_extract_and():
    network = LogicNetwork()
    network.create_pi("a")
    network.create_pi("b")
    network.create_and("c", "a", "b")
    network.create_po("c")
    
    assert network.num_pis == 2
    assert network.num_ands == 1
    assert network.num_pos == 1
    
    circuit = extract(network)
    print(circuit.to_json())
    
    assert circuit.n_qubits == 3
    assert circuit.n_gates == 1
    
    assert circuit.gates[0] == {
        "name": "Tof",
        "ctrl1": 0,
        "ctrl2": 1,
        "target": 2
    }

def test_02_extract_xor():
    network = LogicNetwork()
    network.create_pi("a")
    network.create_pi("b")
    network.create_xor("c", "a", "b")
    network.create_po("c")
    
    assert network.num_pis == 2
    assert network.num_ands == 0
    assert network.num_pos == 1
    
    circuit = extract(network)
    print(circuit.to_json())
    
    assert circuit.n_qubits == 3
    assert circuit.n_gates == 2
    
    assert circuit.gates[0] == {
        "name": "CNOT",
        "ctrl": 0,
        "target": 2
    }
    assert circuit.gates[1] == {
        "name": "CNOT",
        "ctrl": 1,
        "target": 2
    }
    
def test_03_extract_esop():
    network = LogicNetwork()
    network.create_pi("a")
    network.create_pi("b")
    network.create_pi("c")
    network.create_and("and1", "a", "b")
    network.create_and("and2", "a", "c")
    network.create_xor("d", "and1", "and2")
    network.create_po("d")
    
    assert network.num_pis == 3
    assert network.num_ands == 2
    assert network.num_pos == 1
    
    circuit = extract(network)
    print(circuit.to_json())
    
    assert circuit.n_qubits == 4
    assert circuit.n_gates == 2
    
    assert circuit.gates[0] == {
        "name": "Tof",
        "ctrl1": 0,
        "ctrl2": 1,
        "target": 3
    }
    assert circuit.gates[1] == {
        "name": "Tof",
        "ctrl1": 0,
        "ctrl2": 2,
        "target": 3
    }