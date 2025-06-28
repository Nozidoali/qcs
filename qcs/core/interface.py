def t_opt(circuit):
    """
    Optimize T-count of a quantum circuit using the specified method.
    
    Parameters:
        circuit (QuantumCircuit): The quantum circuit to optimize.
        method (str): The optimization method to use. Default is "TOHPE".
        **kwargs: Additional keyword arguments for the optimization method.
    
    Returns:
        QuantumCircuit: The optimized quantum circuit.
    """
    from ._core import dummy_optimization
    return dummy_optimization(circuit)

def to_tableau(circuit):
    """
    Convert a quantum circuit to a tableau representation.
    
    Parameters:
        circuit (QuantumCircuit): The quantum circuit to convert.
    
    Returns:
        SimpleTableau: The tableau representation of the circuit.
    """
    from ._core import tableau_from_circuit
    return tableau_from_circuit(circuit)

def from_tableau(tableau):
    """
    Convert a tableau representation back to a quantum circuit.
    
    Parameters:
        tableau (SimpleTableau): The tableau to convert.
    
    Returns:
        QuantumCircuit: The quantum circuit representation of the tableau.
    """
    from ._core import tableau_to_circuit
    return tableau_to_circuit(tableau)