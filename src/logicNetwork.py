class LogicGate:
    def __init__(self, gate_type: str, inputs: list[str], output: str, data = {}):
        self.gate_type = gate_type
        self.inputs = inputs
        self.output = output
        self.data = data

    @staticmethod
    def from_assignment(assign_str: str, map_or: bool = True) -> "LogicGate":
        # fixme: consider complicated gates
        assign_to, assign_from = map(lambda x: x.strip(), assign_str.split("="))
        for op in ["&", "|", "^"]:
            if op in assign_from:
                s1, s2 = map(lambda x: x.strip(), assign_from.split(op))
                p1, p2, s1, s2 = '~' in s1, '~' in s2, s1.replace("~", ""), s2.replace("~", "")
                if map_or and op == "|":
                    # De Morgan's law
                    return LogicGate("&", [s1, s2], assign_to, {"p1": not p1, "p2": not p2, "p3": True})
                return LogicGate(op, [s1, s2], assign_to, {"p1": p1, "p2": p2, "p3": False})
        p, s = '~' in assign_from, assign_from.replace("~", "")
        return LogicGate("=", [s], assign_to)

    def to_assignment(self) -> str:
        raise NotImplementedError("to_assignment is not implemented")

    def to_json(self) -> dict:
        return {
            "gate_type": self.gate_type,
            "inputs": self.inputs,
            "output": self.output,
            "data": self.data
        }

    @property
    def is_and(self) -> bool:
        return self.gate_type == "&"

    @property
    def is_xor(self) -> bool:
        return self.gate_type == "^"

    @property
    def is_buf(self) -> bool:
        return self.gate_type == "="

    @property
    def is_pi(self) -> bool:
        return len(self.inputs) == 0

def _get_list(lst_str: str, s: str = None) -> list[str]:
    _str = lst_str.replace(s, "").strip()
    return [x.strip() for x in _str.split(",") if x.strip() != ""]

class LogicNetwork:
    def __init__(self):
        self.inputs:  list[str] = []
        self.outputs: list[str] = []
        self.gates: dict[str, LogicGate] = {}
        
        # private
        self._node_fanouts: dict[str, set[str]] = {}
    
    @staticmethod
    def from_verilog(verilog_str: str) -> "LogicNetwork":
        lines = verilog_str.splitlines()
        i, ntk = 0, LogicNetwork()
        while i < len(lines):
            line = lines[i].strip()
            i += 1
            if line.startswith("//") or line == "": continue
            if line.startswith("endmodule"): break
            while not line.endswith(";"):
                line += lines[i].strip()
                i += 1
            line = line.rstrip(";")
            for keyword, lst in [("input", ntk.inputs), ("output", ntk.outputs)]:
                if line.startswith(keyword):
                    lst.extend(_get_list(line, keyword))
                    break
            if line.startswith("assign"):
                gate = LogicGate.from_assignment(_get_list(line, "assign")[0])
                ntk.gates[gate.output] = gate
        ntk._compute_fanouts()
        return ntk
    
    def to_verilog(self) -> str:
        verilog_str = "module top(\n"
        verilog_str += ", ".join(self.inputs + self.outputs) + "\n"
        verilog_str += ");\n"
        verilog_str += "  input "  + ", ".join(self.inputs) + ";\n"
        verilog_str += "  output " + ", ".join(self.outputs) + ";\n"
        verilog_str += "  wire "   + ", ".join([k for k in self.gates.keys() if k not in self.inputs + self.outputs]) + ";\n"
        for gate in self.gates.values():
            verilog_str += gate.to_assignment() + "\n"
        verilog_str += "endmodule\n"
        return verilog_str
    
    @property
    def n_ands(self) -> int:
        return sum(gate.is_and for gate in self.gates.values())
    
    def get_gate(self, node: str) -> LogicGate:
        return self.gates.get(node, None)
    
    def is_pi(self, node: str) -> bool: #TODO: O(1)
        return node in self.inputs
    
    def _compute_fanouts(self):
        for node, gate in self.gates.items():
            for input in gate.inputs:
                if input not in self._node_fanouts:
                    self._node_fanouts[input] = set()
                self._node_fanouts[input].add(node)

    def num_fanouts(self, node: str) -> int:
        return len(self._node_fanouts.get(node, 0))

    def fanouts(self, node: str) -> list[str]:
        return list(self._node_fanouts.get(node, []))


if __name__ == "__main__":
    import os
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    verilog_file = os.path.join(curr_dir, "../data/input/gf_mult2.v")
    verilog = LogicNetwork.from_verilog(open(verilog_file).read())
