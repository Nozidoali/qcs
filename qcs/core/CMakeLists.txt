cmake_minimum_required(VERSION 3.18)
project(qcs_core LANGUAGES CXX)

find_package(pybind11 REQUIRED)

option(QCS_VERBOSE "Enable verbose build messages for QCS" ON)

if(QCS_VERBOSE)
    message(STATUS "🧩 Pybind11 include path: ${pybind11_INCLUDE_DIRS}")
    message(STATUS "🔧 Building QCS core using C++${CMAKE_CXX_STANDARD}")
endif()

file(GLOB SRC CONFIGURE_DEPENDS src/*.cpp)

pybind11_add_module(_core ${SRC})
target_include_directories(_core PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_compile_features(_core PRIVATE cxx_std_20)

# ✅ Install the compiled module to qcs/core
install(TARGETS _core DESTINATION qcs/core)

message(STATUS "✅ Building qcs.core._core from C++ sources")
