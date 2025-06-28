#include "interface.hpp"
#include <pybind11/stl.h>

namespace py = pybind11;

namespace core {

/* ------------------------------------------------------------------------- */
/* Convert Python BitVector to C++ BitVector                           */
/* ------------------------------------------------------------------------- */
BitVector bitvector_from_python(const py::object& py_bitvector)
{
    const auto bools = py_bitvector.attr("get_boolean_vec")().cast<std::vector<bool>>();
    BitVector out(bools.size());
    for (std::size_t i = 0; i < bools.size(); ++i)
        if (bools[i]) out.xor_bit(i);
    return out;
}

/* ------------------------------------------------------------------------- */
/* Convert C++ BitVector to Python BitVector                           */
/* ------------------------------------------------------------------------- */
py::object bitvector_to_python(const BitVector& bv)
{
    static py::object PyBitVector = py::module::import("qcs.common").attr("BitVector");

    py::object py_bv = PyBitVector(py::cast(bv.size()));
    for (std::size_t i = 0; i < bv.size(); ++i)
        if (bv.get(i))
            py_bv.attr("xor_bit")(py::cast(i));
    return py_bv;
}

}  // namespace core
