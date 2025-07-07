from itertools import product
from qcs.common import QuantumCircuit
from qcs.visualization import plot_circuit
from qcs.patternRewriting import pattern_rewrite, apply_rule_based_rewriting


if __name__ == "__main__":
    test_tt = [
        "00011011",  # AND
        "01101001",  # XOR
    ]
    
    test_circuit = QuantumCircuit.from_truth_table(test_tt, n=3, m=2)
    plot_circuit(test_circuit, "qrom_test_circuit.png")

    from rich.pretty import pprint
    pprint(test_circuit.gates)

    optimized_circuit = pattern_rewrite(test_circuit)
    plot_circuit(optimized_circuit, "qrom_test_circuit_optimized.png")
