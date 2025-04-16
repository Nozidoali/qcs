import json

from config import *
from logicNetwork import LogicNetwork

if __name__ == "__main__":
    for name, verilog_in, json_out in BMARKS:
        datas = {"name": name}
        ntk = LogicNetwork.from_verilog(open(verilog_in).read())
        datas["n_ands"] = ntk.n_ands
        open(json_out, "w").write(json.dumps(datas, indent=4))