from pathlib import Path
import sys, time

PROJ_DIR = Path(__file__).parent.parent
INPUT_DIR = (PROJ_DIR / "data" / "input" / "qc").resolve()
sys.path.append((PROJ_DIR / 'src').resolve().__str__())

from quantumCircuit import QuantumCircuit
from thirdOrderPolynomial import t_count_optimization

import pandas as pd

ALL_INPUTS = sorted(INPUT_DIR.glob("*.qc"))

if __name__ == "__main__":
    assert Path.exists(INPUT_DIR), f"Input directory {INPUT_DIR} does not exist."

    datas = []
    for i, file in enumerate(ALL_INPUTS):
        
        name: str = file.stem
        
        # if name not in ["gf_mult2", "gf_mult3", "gf_mult4", "gf_mult5", "gf_mult6", "gf_mult7", "gf_mult8", "gf_mult9", "gf_mult10"]:
        if name not in ["gf_mult2", "gf_mult3", "gf_mult4", "gf_mult5", "gf_mult6"]:
            continue
        
        # if name != "tof_3":
        #     continue
                
        tic = time.time()
        circuit = QuantumCircuit.from_file(file).to_basic_gates()
        print(f"{name}, {circuit.num_t}, {circuit.n_qubits}, {circuit.num_2q}, {circuit.num_internal_h}")
        
        num_internal_h = circuit.num_internal_h
        
        method = "TOHPE"
        if name in ["gf_mult4", "gf_mult5", "gf_mult6"]:
            method = "FastTODD"
        
        circuit = t_count_optimization(circuit, method=method)
        runtime = time.time() - tic
        
        print(f"{name}, {circuit.num_t}, {circuit.n_qubits}, {circuit.num_2q}, {runtime:.2f}, {num_internal_h}")
        datas.append({
            "name": name,
            "t_count": circuit.num_t,
            "n_qubits": circuit.n_qubits,
            "num_2q": circuit.num_2q,
            "runtime": runtime,
            "num_internal_h": num_internal_h,
        })
    df = pd.DataFrame(datas)
    df.to_csv("t_count_optimization_results.csv", index=False)