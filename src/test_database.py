import numpy as np
from phasePolynomial import logic_to_d3, synthesize_d3
from circuitExtract import extract_q_opt
from logicNetwork import LogicNetwork
from visualization import plot_circuit, plot_network
import random
import queue
import pandas as pd
import tqdm

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

import time, math

if __name__ == "__main__":
    datas: list[dict] = []
    n_repeat: int = 10
    
    
    timeout: int = 10
    
    for n in tqdm.tqdm(range(3, 5), desc="n"):
        n_ands_max: int = n * (n - 1) // 2
        n_ands_min: int = math.floor(math.sqrt(n))
        for n_ands in tqdm.tqdm(range(n_ands_min, n_ands_max, 1), desc="n_ands", leave=False):
            for _ in tqdm.tqdm(range(n_repeat), desc="repeat", leave=False):
                try:
                    # Generate a random network
                    network: LogicNetwork = random_network(n, n_ands)
                    
                    start = time.time()
                    circuit = extract_q_opt(network)
                    zx_time = time.time() - start
                    
                    plot_network(network, file_name="random_network.png")
                    plot_circuit(circuit, file_name="random_circuit.png")
                    zx_result = circuit.num_t
                    
                    start = time.time()
                    d3: np.ndarray = logic_to_d3(network)
                    res = synthesize_d3(d3, verbose=False, timeout=timeout)
                    pp_time = time.time() - start

                    if not res: pass
                    else:
                        pp_result, _ = res
                        datas.append({"n": n, "n_and": n_ands, "zx": zx_result, "pp": pp_result, "zx_time": zx_time, "pp_time": pp_time})
                        pd.DataFrame(datas).to_csv(f"random_{timeout}.csv", index=False)
                except: pass