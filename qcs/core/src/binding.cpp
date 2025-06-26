// binding.cpp
#include <pybind11/pybind11.h>
#include "binding.hpp"
#include <algorithm>  // for std::reverse

namespace py = pybind11;

namespace core {

QuantumCircuit from_python_circuit(const py::object& py_circ) {
    QuantumCircuit circ;
    circ.n_qubits = py_circ.attr("n_qubits").cast<uint32_t>();
    py::list py_gates = py_circ.attr("gates");

    for (const auto& item : py_gates) {
        py::dict d = py::cast<py::dict>(item);
        GateType type;
        std::string name = d["name"].cast<std::string>();

        if      (name == "X")    type = GateType::X;
        else if (name == "Z")    type = GateType::Z;
        else if (name == "HAD")  type = GateType::H;
        else if (name == "CNOT") type = GateType::CNOT;
        else if (name == "T")    type = GateType::T;
        else if (name == "Tdg")  type = GateType::Td;
        else if (name == "S")    type = GateType::S;
        else if (name == "Sd")   type = GateType::Sd;
        else if (name == "Tof")  type = GateType::Toffoli;
        else if (name == "Swap") type = GateType::Swap;
        else if (name == "CZ")   type = GateType::CZ;
        else if (name == "CCZ")  type = GateType::Toffoli; // alias
        else throw std::runtime_error("Unknown gate name: " + name);

        uint16_t q1 = d.contains("target") ? d["target"].cast<uint16_t>() : 0;
        uint16_t q2 = d.contains("ctrl")   ? d["ctrl"].cast<uint16_t>()   : 0;
        uint16_t q3 = d.contains("ctrl2")  ? d["ctrl2"].cast<uint16_t>()  : 0;

        Gate g(type, q1, false, q2, false, q3, false);
        circ.gates.push_back(g);
    }
    return circ;
}

py::object to_python_circuit(const QuantumCircuit& circ) {
    py::module qcs = py::module::import("qcs.quantumCircuit");
    py::object py_circ = qcs.attr("QuantumCircuit")();
    py_circ.attr("n_qubits") = circ.n_qubits;
    py::list py_gates;

    for (const auto& g : circ.gates) {
        py::dict d;
        switch (g.type()) {
            case GateType::X:        d["name"] = "X"; break;
            case GateType::Z:        d["name"] = "Z"; break;
            case GateType::H:        d["name"] = "HAD"; break;
            case GateType::CNOT:     d["name"] = "CNOT"; break;
            case GateType::T:        d["name"] = "T"; break;
            case GateType::Td:       d["name"] = "Tdg"; break;
            case GateType::S:        d["name"] = "S"; break;
            case GateType::Sd:       d["name"] = "Sd"; break;
            case GateType::Toffoli:  d["name"] = "Tof"; break;
            case GateType::Swap:     d["name"] = "Swap"; break;
            case GateType::CZ:       d["name"] = "CZ"; break;
            default:                 d["name"] = "UNKNOWN"; break;
        }

        d["target"] = g.qubit1();
        if (g.qubit2() != 0) d["ctrl"] = g.qubit2();
        if (g.qubit3() != 0) d["ctrl2"] = g.qubit3();
        py_gates.append(d);
    }

    py_circ.attr("gates") = py_gates;
    return py_circ;
}

py::object dummy_optimization(const py::object& py_circ) {
    QuantumCircuit circ = from_python_circuit(py_circ);
    std::reverse(circ.gates.begin(), circ.gates.end());
    return to_python_circuit(circ);
}

} // namespace core

namespace py = pybind11;

PYBIND11_MODULE(_core, m) {
    m.doc() = "C++ core backend for qcs";

    m.def("dummy_optimization", &core::dummy_optimization, "A dummy optimization that reverses gates");
}