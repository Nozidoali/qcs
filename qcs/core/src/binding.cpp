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
        else if (name == "Sdg")  type = GateType::Sd;
        else if (name == "Tof")  type = GateType::Toffoli;
        else if (name == "Swap") type = GateType::Swap;
        else if (name == "CZ")   type = GateType::CZ;
        else if (name == "CCZ")  type = GateType::Toffoli; // alias
        else throw std::runtime_error("Unknown gate name: " + name);

        uint16_t q1 = d.contains("target") ? d["target"].cast<uint16_t>() : 0;
        uint16_t q2 = 0, q3 = 0;
        if (d.contains("ctrl1") && d.contains("ctrl2")) {
            q2 = d["ctrl1"].cast<uint16_t>();
            q3 = d["ctrl2"].cast<uint16_t>();
        } else if (d.contains("ctrl")) {
            q2 = d["ctrl"].cast<uint16_t>();
        }

        Gate g(type, q1, false, q2, false, q3, false);
        circ.gates.push_back(g);
    }
    return circ;
}

py::object to_python_circuit(const QuantumCircuit& circ) {
    py::module common = py::module::import("qcs.common");
    py::object py_circ = common.attr("QuantumCircuit")();
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
            case GateType::Sd:       d["name"] = "Sdg"; break;
            case GateType::Toffoli:  d["name"] = "Tof"; break;
            case GateType::Swap:     d["name"] = "Swap"; break;
            case GateType::CZ:       d["name"] = "CZ"; break;
            default:                 d["name"] = "UNKNOWN"; break;
        }

        d["target"] = g.qubit1();
        // Set control qubits based on gate type
        if (g.type() == GateType::CNOT || g.type() == GateType::CZ) {
            d["ctrl"] = g.qubit2();
        } else if (g.type() == GateType::Toffoli) {
            d["ctrl1"] = g.qubit2();
            d["ctrl2"] = g.qubit3();
        }
        py_gates.append(d);
    }

    py_circ.attr("gates") = py_gates;
    return py_circ;
}

py::object dummy_optimization(const py::object& py_circ) {
    QuantumCircuit circ = from_python_circuit(py_circ);
    QuantumCircuit hadamard_free_circuit = gadgetize_internal_hadamards(circ);
    core::TOptimizer opt(hadamard_free_circuit.n_qubits);
    auto optimised = opt.optimize(hadamard_free_circuit, "TOHPE");
    return to_python_circuit(optimised);
}


/* ------------------------------------------------------------------------- */
/*  Helper: build a BitVector from a '0'/'1' string                          */
core::BitVector make_bitvec(const std::string& bits)
{
    core::BitVector v(bits.size());
    for (std::size_t i = 0; i < bits.size(); ++i)
        if (bits[i] == '1') v.xor_bit(i);      // toggle into ‘1’
    return v;
}

/* ------------------------------------------------------------------------- */
/*  Conversion: Python tableau  →  C++ RowMajorTableau                       */
/*    Accepts either                                                         */
/*       • an object with attributes  z_rows, x_rows, signs                  */
/*       • or a 3-tuple  (z_rows, x_rows, signs)                             */
core::RowMajorTableau tableau_from_py(const py::object& src)
{
    std::vector<std::string> z_rows;
    std::vector<std::string> x_rows;
    std::string              signs;

    /* ---- 1.  Extract the three bit-string containers from Python -------- */
    if (py::hasattr(src, "z_rows") && py::hasattr(src, "x_rows"))
    {
        z_rows = src.attr("z_rows").cast<std::vector<std::string>>();
        x_rows = src.attr("x_rows").cast<std::vector<std::string>>();
        signs  = src.attr("signs" ).cast<std::string>();
    }
    else                                    // assume a tuple-like object
    {
        auto tup = src.cast<py::tuple>();
        if (tup.size() != 3)
            throw std::runtime_error("Expect (z_rows, x_rows, signs)");
        z_rows = tup[0].cast<std::vector<std::string>>();
        x_rows = tup[1].cast<std::vector<std::string>>();
        signs  = tup[2].cast<std::string>();
    }

    /* ---- 2.  Sanity checks --------------------------------------------- */
    if (z_rows.empty())
        throw std::runtime_error("Tableau must have at least one row");
    if (z_rows.size() != x_rows.size())
        throw std::runtime_error("z_rows and x_rows row-count mismatch");

    const std::size_t row_len = z_rows.front().size();
    for (auto& s : z_rows)
        if (s.size() != row_len) throw std::runtime_error("Inconsistent z_row length");
    for (auto& s : x_rows)
        if (s.size() != row_len) throw std::runtime_error("Inconsistent x_row length");
    if (signs.size() != row_len)
        throw std::runtime_error("signs length must equal row width");
    if (row_len % 2)
        throw std::runtime_error("Row width must be even (it should equal 2·n_qubits)");

    const std::size_t n_qubits = row_len / 2;
    if (z_rows.size() != n_qubits)
        throw std::runtime_error("Expect exactly n_qubits rows (minimal generator set)");

    /* ---- 3.  Build a fresh C++ tableau, then overwrite each column ------ */
    core::RowMajorTableau tab(n_qubits);     // starts as identity

    for (std::size_t col = 0; col < row_len; ++col)
    {
        core::BitVector z_col(n_qubits);
        core::BitVector x_col(n_qubits);

        for (std::size_t row = 0; row < n_qubits; ++row)
        {
            if (z_rows[row][col] == '1') z_col.xor_bit(row);
            if (x_rows[row][col] == '1') x_col.xor_bit(row);
        }
        bool sign_bit = (signs[col] == '1');

        core::PauliProduct pp(std::move(z_col), std::move(x_col), sign_bit);
        tab.insert_pauli_product(pp, col);
    }
    return tab;
}

/* ------------------------------------------------------------------------- */
/*  Reverse conversion: C++ tableau → Python (z_rows, x_rows, signs)         */
py::object tableau_to_py(const core::RowMajorTableau& tab)
{
    const std::size_t n       = tab.n_qubits();
    const std::size_t row_len = 2 * n;

    /* --- collect bit-strings ------------------------------------------- */
    std::vector<std::string> z_rows(n, std::string(row_len, '0'));
    std::vector<std::string> x_rows(n, std::string(row_len, '0'));
    std::string              signs(row_len, '0');

    for (std::size_t r = 0; r < n; ++r)
        for (std::size_t c = 0; c < row_len; ++c) {
            if (tab.z_row(r).get(c)) z_rows[r][c] = '1';
            if (tab.x_row(r).get(c)) x_rows[r][c] = '1';
        }
    for (std::size_t c = 0; c < row_len; ++c)
        if (tab.sign_bit(c)) signs[c] = '1';

    /* --- construct SimpleTableau object in Python ----------------------- */
    py::module common = py::module::import("qcs.common");
    py::object py_tableau = common.attr("RowMajorTableau")(
        py::cast(z_rows),     // positional-arg: z_rows
        py::cast(x_rows),     // positional-arg: x_rows
        py::cast(signs));     // positional-arg: signs

    return py_tableau;
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

} // namespace core

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