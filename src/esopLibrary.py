from rich.pretty import pprint

from logicNetwork import LogicNetwork
from visualization import plot_network, plot_circuit
from circuitExtract import extract_q_opt

if __name__ == "__main__":
    import os
    from rich.pretty import pprint
    
    benchmark: str = "gf_mult2"
    
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    verilog_file = os.path.join(curr_dir, f"../data/input/{benchmark}.v")
    network = LogicNetwork.from_verilog(open(verilog_file).read())
    circuit = extract_q_opt(network)
    
    plot_network(network,     file_name=f"{benchmark}_network.png")
    plot_circuit(circuit, file_name=f"{benchmark}_circuit.png")
    
    datas = {"n_ands": network.n_ands, "n_t": circuit.num_t, "n_qubits": circuit.n_qubits}
    pprint(datas)