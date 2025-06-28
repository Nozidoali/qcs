import queue, random

class LogicGate:
    def __init__(self, gate_type: str, inputs: list[str], output: str, data = {}):
        self.gate_type: str = gate_type
        self.inputs: list[str] = inputs
        self.output: list[str] = output
        self.data: dict = data

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
        raise NotImplementedError("verilog output is not implemented")

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
        self._name: dict[str, str] = {}
        self._node_patterns: dict[str, int] = {}
    
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
        ntk._rename()
        ntk._compute_fanouts()
        return ntk
    
    def to_verilog(self) -> str:
        verilog_str  = "module top(\n"
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
    
    @property
    def n_pos(self) -> int:
        return len(self.outputs)
    
    @property
    def n_pis(self) -> int:
        return len(self.inputs)
    
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
                
    def _rename(self):
        _gates: dict[str, LogicGate] = {}
        for node, gate in self.gates.items():
            _name = f"n{len(_gates)}"
            self._name[node] = _name
            _inputs = [self._name.get(i, i) for i in gate.inputs]
            _gates[_name] = LogicGate(gate.gate_type, _inputs, _name, gate.data)
        _outputs: list[str] = [self._name.get(o, o) for o in self.outputs]
        self.outputs = _outputs
        self.gates = _gates
                
    def num_fanouts(self, node: str) -> int:
        return len(self._node_fanouts.get(node, 0))

    def fanouts(self, node: str) -> list[str]:
        return list(self._node_fanouts.get(node, []))
    
    def fanins(self, node: str) -> list[str]:
        return [] if node in self.inputs else self.gates[node].inputs
    
    def create_pi(self, node: str) -> None:
        self.inputs.append(node)

    def create_po(self, node: str) -> None:
        self.outputs.append(node)
        
    def create_and(self, n: str, f1: str, f2: str) -> None:
        self.gates[n] = LogicGate("&", [f1, f2], n, {"p1": False, "p2": False, "p3": False})
        
    def create_xor(self, n: str, f1: str, f2: str) -> None:
        self.gates[n] = LogicGate("^", [f1, f2], n, {"p1": False, "p2": False, "p3": False})

    def has(self, node: str) -> bool:
        return node in self.gates or node in self.inputs
    
    def is_gate(self, node: str) -> bool:
        return node in self.gates

    def clone_gate(self, gate: LogicGate) -> None:
        _gate = LogicGate(gate.gate_type, gate.inputs[:], gate.output, gate.data.copy())
        self.gates[_gate.output] = _gate
        
    def simulate(self) -> int:
        if self.n_pis >= 5:
            raise NotImplementedError("Simulation for more than 5 inputs is not implemented")
        mask: int = (1<<(1<<self.n_pis)) - 1
        for i, _i in enumerate(self.inputs):
            self._node_patterns[_i] = 0
            for x in range(1 << self.n_pis):
                if ((x >> i) & 1) == 1: self._node_patterns[_i] |= (1 << x)
            self._node_patterns[_i] &= mask
        for _n, gate in self.gates.items():
            if gate.is_and:
                _p1, _p2 = map(lambda x: self._node_patterns[x], gate.inputs)
                _p1 = ~_p1 & mask if gate.data["p1"] else _p1
                _p2 = ~_p2 & mask if gate.data["p2"] else _p2
                self._node_patterns[_n] = ~(_p1 & _p2) & mask if gate.data["p3"] else _p1 & _p2
            elif gate.is_buf:
                _p1 = self._node_patterns[gate.inputs[0]]
                self._node_patterns[_n] = ~_p1 & mask if gate.data["p1"] else _p1
            elif gate.is_xor:
                _p1, _p2 = map(lambda x: self._node_patterns[x], gate.inputs)
                _p1 = ~_p1 & mask if gate.data["p1"] else _p1
                _p2 = ~_p2 & mask if gate.data["p2"] else _p2
                self._node_patterns[_n] = (_p1 ^ _p2) & mask if gate.data["p3"] else ~(_p1 ^ _p2) & mask
            else:
                raise NotImplementedError("Simulation for this gate is not implemented")
    
    def get_pattern(self, node: str) -> int:
        if node not in self._node_patterns:
            raise ValueError(f"Node {node} not found in the network")
        return self._node_patterns[node]

def random_network(n: int, n_gates: int) -> LogicNetwork:
    network = LogicNetwork()
    for _ in range(n): network.create_pi(f"pi{_}")
    and_queue: set[tuple[int, int]] = set()
    xor_queue: queue.Queue = queue.Queue()
    while len(and_queue) < n_gates:
        n1, n2 = random.sample(range(n), 2)
        if (n1, n2) not in and_queue and (n2, n1) not in and_queue:
            network.create_and(f"n{len(and_queue)}", f"pi{n1}", f"pi{n2}")
            xor_queue.put(f"n{len(and_queue)}")
            and_queue.add((n1, n2))
    idx: int = len(and_queue)
    while xor_queue.qsize() > 1:
        n1, n2 = xor_queue.get(), xor_queue.get()
        network.create_xor(f"n{idx}", n1, n2)
        xor_queue.put(f"n{idx}")
        idx += 1
    network.create_po(xor_queue.get())
    network._compute_fanouts()
    return network

if __name__ == "__main__":
    import os
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    verilog_file = os.path.join(curr_dir, "../data/input/gf_mult2.v")
    verilog = LogicNetwork.from_verilog(open(verilog_file).read())
