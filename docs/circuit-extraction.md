Circuit extraction from logic network
=====================================

Cut enumeration and T cost estimation
-------------------------------------

We apply cut merging algorithm to collect all the cuts that are implementable using only one ancilla qubit. This involves checking the reversibility of the functionality (idea: maybe we could extend this to multiple outputs). For each cut, we map the subnetwork to its ESOP form and then map AND terms to Toffoli. We apply then the optimization script in the zx calculus to find the optimal T count for the subcircuit (idea: we can also extend the phase polynomial simplification algorithm to find the optimal T count). Note that we are not considering the context of the subcircuit right now, meaning we are missing some optimization opportunities. 

Approximate logic synthesis
---------------------------


