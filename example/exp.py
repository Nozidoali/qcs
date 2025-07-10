import qcs
from qcs.common import QuantumCircuit
from qcs.fastTODD import fast_todd_optimize

import pandas as pd
import os, json

best_result_dir = "./data/output/topt/"
best_gf_mult_results = os.path.join(best_result_dir, "gf_mult_results.json")


if __name__ == "__main__":
    if not os.path.exists(best_result_dir):
        os.makedirs(best_result_dir)
    
    if os.path.exists(best_gf_mult_results):
        best_results = json.loads(open(best_gf_mult_results).read())
    else:
        best_results = {}
    
    datas = []
    for n in range(2, 10):
        
        # print("\n\n\n")
        # print(f"Processing gf_mult{n} circuit...")

        circuit: QuantumCircuit = qcs.QuantumCircuit.from_file(f"./data/input/qc/gf_mult{n}.qc")
        
        circuit_baseline = fast_todd_optimize(circuit)
        data = {
            "n": n,
            "num_qubits_baseline": circuit.n_qubits,
            "num_2q_baseline": circuit_baseline.num_2q, 
            "num_t_baseline": circuit_baseline.num_t,
        }
        
        circuit: QuantumCircuit = qcs.QuantumCircuit.from_file(f"./data/input/qc/gf_mult{n}.qc")
        circuit_ours = qcs.iterative_gadgetization(circuit)
        circuit_ours = fast_todd_optimize(circuit_ours)
        circuit_ours = circuit_ours.optimize_cnot_regions()
        data.update({
            "num_qubits_ours": circuit_ours.n_qubits,
            "num_2q_ours": circuit_ours.num_2q, 
            "num_t_ours": circuit_ours.num_t,
        })
        
        datas.append(data)
        
        if str(n) not in best_results:
            prev_best = circuit_ours.num_t
        else:
            prev_best = best_results[str(n)]["num_t_ours"]
            
        if circuit_ours.num_t <= prev_best:
            best_results[str(n)] = {
                "num_qubits_baseline": circuit.n_qubits,
                "num_2q_baseline": circuit_baseline.num_2q, 
                "num_t_baseline": circuit_baseline.num_t,
                "num_qubits_ours": circuit_ours.n_qubits,
                "num_2q_ours": circuit_ours.num_2q, 
                "num_t_ours": circuit_ours.num_t,
            }
            
            # Save the best circuit
            open(os.path.join(best_result_dir, f"gf_mult{n}_ours.qc"), "w").write(circuit_ours.to_qc())
        
        pd.DataFrame(datas).to_csv("exp.csv", index=False)
        open(best_gf_mult_results, "w").write(json.dumps(best_results, indent=4))