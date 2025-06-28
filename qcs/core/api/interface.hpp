// binding.hpp
#pragma once

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "circuit.hpp"
#include "gate.hpp"
#include "gadgetization.hpp"
#include "hadamardOptimization.hpp"
#include "tOptimizer.hpp"

namespace core {

// Convert from Python QuantumCircuit (Python class) to C++ QuantumCircuit
QuantumCircuit from_python_circuit(const pybind11::object& py_circ);

// Convert from C++ QuantumCircuit to Python QuantumCircuit object
pybind11::object to_python_circuit(const QuantumCircuit& circ);

/* Convert a Python tableau (SimpleTableau or (z_rows, x_rows, signs) tuple)
   into a fully-constructed core::RowMajorTableau. */
RowMajorTableau tableau_from_py(const pybind11::object& src);

/* Inverse conversion: C++ tableau → 3-tuple (z_rows, x_rows, signs). */
pybind11::object tableau_to_py(const core::RowMajorTableau& tab);

// Dummy optimization pass (for testing)
pybind11::object dummy_optimization(const pybind11::object& py_circ);

// synthesis a tableau from a Python circuit
pybind11::object tableau_to_circuit(const pybind11::object& src);

// get the tableau of a Python circuit
pybind11::object tableau_from_circuit(const pybind11::object& src);

/// Convert a Python BitVector (expects get_boolean_vec()) to C++ core::BitVector.
BitVector bitvector_from_python(const pybind11::object& py_bv);

/// Convert a C++ core::BitVector to Python BitVector (qcs.common.BitVector).
pybind11::object bitvector_to_python(const BitVector& bv);

} // namespace core
