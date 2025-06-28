// binding.cpp
#include <pybind11/pybind11.h>
#include "interface.hpp"
#include <algorithm>  // for std::reverse

namespace py = pybind11;

/* ────────────────────────────────────────────────────────────────────────── */
/*  pybind11 module definition                                               */
/* ────────────────────────────────────────────────────────────────────────── */
PYBIND11_MODULE(_core, m)
{
    m.doc() = "C++ core backend for qcs";

    /* previously-bound helpers ------------------------------------------- */
    m.def("dummy_optimization", &core::dummy_optimization,
          "A dummy optimization that reverses gates");

    /* NEW bindings -------------------------------------------------------- */
    m.def("tableau_to_circuit",   &core::tableau_to_circuit,
          py::arg("tableau"),
          "Convert a (Python) tableau object or (z_rows, x_rows, signs) tuple "
          "into a QuantumCircuit object");

    m.def("tableau_from_circuit",   &core::tableau_from_circuit,
          py::arg("circuit"),
          "Convert a QuantumCircuit into its Row-major stabiliser tableau\n"
          "and return (z_rows, x_rows, signs) as Python strings");
}