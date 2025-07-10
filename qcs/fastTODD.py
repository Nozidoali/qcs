from qcs.common import QuantumCircuit

def fast_todd_optimize(circuit: QuantumCircuit) -> QuantumCircuit:
    import os
    import subprocess
    
    qcfile = "tmp.qc"
    qcfileout = "output.qc"
    
    qcstr = circuit.to_qc()
    try:
        open(qcfile, "w").write(qcstr)
        subprocess.run("quantum_circuit_optimization FastTMerge InternalHOpt FastTODD {} > /dev/null".format(qcfile), shell=True, check=True)
        _circuit = QuantumCircuit.from_file(qcfileout)
        os.remove(qcfile)
        os.remove(qcfileout)
        
    except:
        print("FastTODD optimization failed, using original circuit.")
        print(qcstr)
        _circuit = circuit
        
    return _circuit
    
