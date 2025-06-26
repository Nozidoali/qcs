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

// Dummy optimization pass (for testing)
pybind11::object dummy_optimization(const pybind11::object& py_circ);

} // namespace core
