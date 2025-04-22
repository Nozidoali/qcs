import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', "src")))

from quantumCircuit import QuantumCircuit

def circuit1():
    qc = QuantumCircuit()
    qc.request_qubits(6)
    qc.add_toffoli(0, 2, 4, clean=True)
    qc.add_toffoli(1, 3, 4)
    qc.add_toffoli(1, 2, 5, clean=True)
    qc.add_toffoli(0, 3, 5)
    qc.add_toffoli(1, 3, 5)
    return qc

def circuit2():
    qc = QuantumCircuit()
    qc.request_qubits(6)
    qc.add_toffoli(0, 2, 4, clean=True)
    qc.add_cnot(4, 5)
    qc.add_toffoli(1, 3, 4)
    qc.add_cnot(0, 1)
    qc.add_cnot(2, 3)
    qc.add_toffoli(1, 3, 5)
    qc.add_cnot(0, 1)
    qc.add_cnot(2, 3)
    return qc

# qc = circuit1()
qc = circuit2()
