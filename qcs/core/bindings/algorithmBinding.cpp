#include <pybind11/pybind11.h>
#include "interface.hpp"

namespace py = pybind11;

namespace core {

py::object dummy_optimization(const py::object& py_circ) {
    QuantumCircuit circ = from_python_circuit(py_circ);
    QuantumCircuit hadamard_free_circuit = gadgetize_internal_hadamards(circ);
    auto optimised = optimize_t_gates(hadamard_free_circuit);
    return to_python_circuit(optimised);
}

/* ------------------------------------------------------------------------- */
py::object tableau_to_circuit(const py::object& src) {
    core::RowMajorTableau tab = tableau_from_py(src);
    QuantumCircuit circ = tab.to_circ();
    return to_python_circuit(circ);
}

/* ------------------------------------------------------------------------- */
py::object tableau_from_circuit(const py::object& src) {
    QuantumCircuit circ = from_python_circuit(src);
    core::RowMajorTableau tab = core::RowMajorTableau::from_circ(circ);
    return tableau_to_py(tab);
}

}