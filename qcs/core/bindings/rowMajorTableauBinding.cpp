#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "interface.hpp"

namespace py = pybind11;

namespace core {
    
RowMajorTableau tableau_from_py_strings(
    const std::vector<std::string>& z_rows,
    const std::vector<std::string>& x_rows,
    const std::string&              signs)
{
    if (z_rows.empty())
        throw std::runtime_error("Tableau must have at least one row");

    if (z_rows.size() != x_rows.size())
        throw std::runtime_error("z_rows and x_rows row-count mismatch");

    std::size_t n_rows = z_rows.size();
    std::size_t row_len = z_rows[0].size();

    for (const auto& s : z_rows)
        if (s.size() != row_len)
            throw std::runtime_error("Inconsistent z_row length");

    for (const auto& s : x_rows)
        if (s.size() != row_len)
            throw std::runtime_error("Inconsistent x_row length");

    if (signs.size() != row_len)
        throw std::runtime_error("signs length must equal row width");

    if (row_len % 2 != 0)
        throw std::runtime_error("Row width must be even (should equal 2·n_qubits)");

    std::size_t n_qubits = row_len / 2;
    if (n_rows != n_qubits)
        throw std::runtime_error("Expect exactly n_qubits rows (minimal generator set)");

    RowMajorTableau tab(n_qubits);  // initializes to identity tableau

    for (std::size_t col = 0; col < row_len; ++col) {
        BitVector z_col(n_qubits);
        BitVector x_col(n_qubits);

        for (std::size_t row = 0; row < n_qubits; ++row) {
            if (z_rows[row][col] == '1') z_col.xor_bit(row);
            if (x_rows[row][col] == '1') x_col.xor_bit(row);
        }

        bool sign_bit = (signs[col] == '1');
        PauliProduct pp(std::move(z_col), std::move(x_col), sign_bit);
        tab.insert_pauli_product(pp, col);
    }

    return tab;
}

/* --------------------------------------------------------------------- */
/*  Python tableau (BitVectors or legacy)  →  C++ RowMajorTableau        */
/* --------------------------------------------------------------------- */
RowMajorTableau tableau_from_py(const py::object& src)
{
    /* 1. detect style --------------------------------------------------- */
    const bool has_bitvec_rows = py::hasattr(src, "z") && py::hasattr(src, "x");

    std::vector<std::string> z_rows, x_rows;
    std::string              signs;

    if (!has_bitvec_rows) {
        // ── legacy format: list[str] ──
        if (py::hasattr(src, "z_rows"))
        {
            z_rows = src.attr("z_rows").cast<std::vector<std::string>>();
            x_rows = src.attr("x_rows").cast<std::vector<std::string>>();
            signs  = src.attr("signs").cast<std::string>();
        }
        else {
            auto tup = src.cast<py::tuple>();
            if (tup.size() != 3)
                throw std::runtime_error("Expect (z_rows, x_rows, signs)");
            z_rows = tup[0].cast<std::vector<std::string>>();
            x_rows = tup[1].cast<std::vector<std::string>>();
            signs  = tup[2].cast<std::string>();
        }
    } else {
        // ── BitVector-based object ──
        py::list z_list = src.attr("z");
        py::list x_list = src.attr("x");
        py::object py_signs = src.attr("signs");

        std::size_t n_qubits = z_list.size();
        std::size_t row_len  = py_signs.attr("size")().cast<std::size_t>();

        auto bv_to_str = [row_len](const py::object& bv) {
            BitVector cpp_bv = bitvector_from_python(bv);
            std::string out(row_len, '0');
            for (std::size_t i = 0; i < row_len; ++i)
                if (cpp_bv.get(i)) out[i] = '1';
            return out;
        };

        for (std::size_t r = 0; r < n_qubits; ++r) {
            z_rows.emplace_back(bv_to_str(z_list[r]));
            x_rows.emplace_back(bv_to_str(x_list[r]));
        }
        signs = bv_to_str(py_signs);
    }

    return tableau_from_py_strings(z_rows, x_rows, signs);
}


/* --------------------------------------------------------------------- */
/*  C++ tableau  →  Python RowMajorTableau with BitVectors               */
/* --------------------------------------------------------------------- */
py::object tableau_to_py(const RowMajorTableau& tab)
{
    const std::size_t n   = tab.n_qubits();
    const std::size_t len = 2 * n;

    py::module mod_common   = py::module::import("qcs.common");
    py::object PyTableau    = mod_common.attr("RowMajorTableau");

    py::list z_list, x_list;
    for (std::size_t r = 0; r < n; ++r) {
        z_list.append(bitvector_to_python(tab.z_row(r)));
        x_list.append(bitvector_to_python(tab.x_row(r)));
    }

    py::object py_signs = bitvector_to_python(tab.signs());
    py::object py_tab = PyTableau(py::cast(n));  // constructor initializes identity tableau

    py_tab.attr("z")     = z_list;
    py_tab.attr("x")     = x_list;
    py_tab.attr("signs") = py_signs;

    return py_tab;
}

} // namespace core
