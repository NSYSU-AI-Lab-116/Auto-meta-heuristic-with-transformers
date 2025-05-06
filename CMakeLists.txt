cmake_minimum_required(VERSION 3.10)
project(hh_core LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)

# 設定構建類型
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release CACHE STRING
        "Choose the type of build, options are: Release, Debug, RelWithDebInfo, MinSizeRel."
        FORCE)
endif()

# Find OpenMP
find_package(OpenMP)

# Determine architecture
if(CMAKE_SYSTEM_PROCESSOR MATCHES "aarch64")
    set(ARCH_FLAG "-march=arm64") # aarch64 is often compatible with arm64
elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "x86_64")
    set(ARCH_FLAG "-march=x86-64")
else()
    set(ARCH_FLAG "") # Leave empty for generic architecture
endif()

# 設定編譯器選項
if(CMAKE_BUILD_TYPE MATCHES Debug)
    if(OpenMP_FOUND)
        add_compile_options(-O1 -g -fopenmp)
        target_link_libraries(${PROJECT_NAME} OpenMP::OpenMP_CXX)
    else()
        add_compile_options(-O1 -g)
    endif()
else()
    if(OpenMP_FOUND)
        add_compile_options(-O3 ${ARCH_FLAG} -fopenmp)
        target_link_libraries(${PROJECT_NAME} OpenMP::OpenMP_CXX)
    else()
        add_compile_options(-O3 ${ARCH_FLAG})
    endif()
endif()

# 設定輸出目錄
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${PROJECT_SOURCE_DIR}/src/cpp/build")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${PROJECT_SOURCE_DIR}/src/cpp/build")

# 尋找 Eigen3
find_package(Eigen3 3.3 REQUIRED)
include_directories(${EIGEN3_INCLUDE_DIR})

# 添加 pybind11 子模組
add_subdirectory(extern/pybind11)

# 尋找所有 cpp 檔案
file(GLOB ALG_SRCS "${PROJECT_SOURCE_DIR}/src/cpp/*.cpp")

# 針對每個 cpp 檔案建立模組
foreach(SRC ${ALG_SRCS})
    get_filename_component(ALG ${SRC} NAME_WE)
    pybind11_add_module(${ALG}_cpp ${SRC})
    set_target_properties(${ALG}_cpp PROPERTIES
        LIBRARY_OUTPUT_DIRECTORY "${CMAKE_LIBRARY_OUTPUT_DIRECTORY}"
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}"
    )

    # 添加安裝規則
    install(TARGETS ${ALG}_cpp
        LIBRARY DESTINATION lib
        RUNTIME DESTINATION bin
    )
endforeach()