cmake_minimum_required(VERSION 3.10)
project(hh_core LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release CACHE STRING
        "Choose the type of build, options are: Release, Debug, RelWithDebInfo, MinSizeRel."
        FORCE)
endif()

# Find OpenMP
find_package(OpenMP)

# Determine architecture
if(CMAKE_SYSTEM_PROCESSOR MATCHES "aarch64")
    set(ARCH_FLAG "-march=arm64")
elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "x86_64")
    set(ARCH_FLAG "-march=x86-64")
else()
    set(ARCH_FLAG "") # Leave empty for generic architecture
endif()

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


set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${PROJECT_SOURCE_DIR}/src/cpp/build")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${PROJECT_SOURCE_DIR}/bin")


find_package(Eigen3 3.3 REQUIRED)
include_directories(${EIGEN3_INCLUDE_DIR})


add_subdirectory(extern/pybind11)


file(GLOB ALG_SRCS "${PROJECT_SOURCE_DIR}/src/cpp/*.cpp")

# Create a list to hold all the library target names
set(ALL_TARGETS "")


foreach(SRC ${ALG_SRCS})
    get_filename_component(ALG ${SRC} NAME_WE)
    pybind11_add_module(${ALG}_cpp ${SRC})
    set_target_properties(${ALG}_cpp PROPERTIES
        LIBRARY_OUTPUT_DIRECTORY "${CMAKE_LIBRARY_OUTPUT_DIRECTORY}"
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}"
    )


    install(TARGETS ${ALG}_cpp
        LIBRARY DESTINATION lib
        RUNTIME DESTINATION bin
    )

    # Add the target name to the list
    list(APPEND ALL_TARGETS ${ALG}_cpp)
endforeach()

# Custom target to clean the library output directory
add_custom_target(clean_library_output
    COMMAND ${CMAKE_COMMAND} -E remove_directory "${CMAKE_LIBRARY_OUTPUT_DIRECTORY}"
    COMMAND ${CMAKE_COMMAND} -E make_directory "${CMAKE_LIBRARY_OUTPUT_DIRECTORY}"
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Cleaning the library output directory"
)

# Create a custom target that depends on all the library targets
add_custom_target(all_targets
    DEPENDS ${ALL_TARGETS}
)

# Ensure that 'clean_library_output' is executed before 'all_targets'
add_dependencies(all_targets clean_library_output)

# Make 'all_targets' the default target
set_property(GLOBAL PROPERTY DEFAULT_TARGET all_targets)