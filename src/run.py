import json

from config import *
from logicNetwork import LogicNetwork
from circuitExtract import extract

if __name__ == "__main__":
    for name, verilog_in, circuit_out, json_out in BMARKS:
        ntk = LogicNetwork.from_verilog(open(verilog_in).read())
        circuit = extract(ntk)
        open(circuit_out, "w").write(json.dumps(circuit.to_json(), indent=4))
        datas = {"name": name, "n_ands": ntk.n_ands, "n_t": circuit.num_t(), "n_qubits": circuit.n_qubits}
        open(json_out, "w").write(json.dumps(datas, indent=4))