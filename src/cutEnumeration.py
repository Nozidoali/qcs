from logicNetwork import LogicGate, LogicNetwork
from quantumCircuit import QuantumCircuit
from circuitExtract import xor_block_grouping

if __name__ == "__main__":
    import os
    from rich.pretty import pprint
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    verilog_file = os.path.join(curr_dir, "../data/input/gf_mult2.v")
    network = LogicNetwork.from_verilog(open(verilog_file).read())
    cuts = enumerate_cuts(network)
    pprint(cuts)
    subnetwork = extract_subnetwork(network, "po0", ["pi1", "pi2", "pi3", "pi4"])
