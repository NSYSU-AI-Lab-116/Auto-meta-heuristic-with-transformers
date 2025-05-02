cmake_minimum_required(VERSION 3.15)
project(hh_core LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
add_compile_options(-O3 -march=native -fopenmp)
find_package(Eigen3 3.3 REQUIRED NO_MODULE)
include_directories(${EIGEN3_INCLUDE_DIR})
add_subdirectory(extern/pybind11)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${PROJECT_SOURCE_DIR}/src/cpp/build")
# On Windows
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${PROJECT_SOURCE_DIR}/src/cpp/build")
file(GLOB ALG_SRCS "${PROJECT_SOURCE_DIR}/src/cpp/*.cpp")

foreach(SRC ${ALG_SRCS})
    get_filename_component(ALG ${SRC} NAME_WE)
    pybind11_add_module(${ALG}_cpp ${SRC})
    set_target_properties(${ALG}_cpp PROPERTIES
        LIBRARY_OUTPUT_DIRECTORY "${PROJECT_SOURCE_DIR}/src/cpp/build"
        RUNTIME_OUTPUT_DIRECTORY "${PROJECT_SOURCE_DIR}/src/cpp/build"
    )
endforeach()