# Using the same minimum as the godot-cpp project
cmake_minimum_required(VERSION 3.17)

# Silence unused variable warning when specified from toolchain
if(CMAKE_C_COMPILER)
endif()

set(LIBNAME "scripts") # "The name of the library"
set(GODOT_PROJECT_DIR "project" CACHE STRING "The directory of a Godot project folder")

# Make sure all the dependencies are satisfied
find_package(Python3 3.4 REQUIRED)

add_subdirectory(external/godot-cpp SYSTEM)

# When compiling for emscripten, this toolchainhack needs to be included.
# set(CMAKE_PROJECT_<project-name>_INCLUDE ${godot-cpp_SOURCE_DIR}/cmake/emsdkHack.cmake)

# Create the gen directory at configure time so IDEs can see generated headers immediately after generate_bindings
file(MAKE_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/godot-cpp/gen/include")

# Add godot-cpp's module path and include the exported functions.
# This is made available for documentation generation
set(CMAKE_MODULE_PATH "${CMAKE_MODULE_PATH};${godot-cpp_SOURCE_DIR}/cmake")
include(GodotCPPModule)

# The godot-cpp target has some of useful properties attached that can be retrieved like so.
get_target_property(GODOTCPP_SUFFIX godot::cpp GODOTCPP_SUFFIX)
get_target_property(GODOTCPP_PLATFORM godot::cpp GODOTCPP_PLATFORM)

# Now we can specify our own project which will inherit any global cmake properties or variables that have been defined.
project(godot-cpp-template
    VERSION 1.0
    DESCRIPTION "This repository serves as a quickstart template for GDExtension development with Godot 4.0+."
    HOMEPAGE_URL "https://github.com/enetheru/godot-cpp-template/tree/main"
    LANGUAGES CXX
)

add_library(${LIBNAME} SHARED)

file(GLOB_RECURSE SOURCES CONFIGURE_DEPENDS src/*.c**)
target_sources(${LIBNAME}
    PRIVATE
    ${SOURCES}
)

# Fetch a list of the xml files to use for documentation and add to our target
file(GLOB_RECURSE DOC_XML LIST_DIRECTORIES NO CONFIGURE_DEPENDS "${PROJECT_SOURCE_DIR}/doc_classes/*.xml")

# conditionally add doc data to compile output
if(DOC_XML)
    if(GODOTCPP_TARGET MATCHES "editor|template_debug")
        target_doc_sources(${LIBNAME} "${DOC_XML}")
    endif()
endif()

target_link_libraries(${LIBNAME} PRIVATE godot-cpp)

# Require at least C++17 for this target
set_property(TARGET ${LIBNAME} PROPERTY CXX_STANDARD 17)

set_target_properties(${LIBNAME}
    PROPERTIES
    # The generator expression here prevents msvc from adding a Debug or Release subdir.
    RUNTIME_OUTPUT_DIRECTORY "$<1:${PROJECT_SOURCE_DIR}/../bin/${GODOTCPP_PLATFORM}>"

    PREFIX ""
    OUTPUT_NAME "${LIBNAME}${GODOTCPP_SUFFIX}"
)

set(GODOT_PROJECT_BINARY_DIR "${PROJECT_SOURCE_DIR}/${GODOT_PROJECT_DIR}/../bin/${GODOTCPP_PLATFORM}")

add_custom_command(TARGET ${LIBNAME} POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy "$<TARGET_FILE:${LIBNAME}>" "${GODOT_PROJECT_BINARY_DIR}/$<TARGET_FILE_NAME:${LIBNAME}>"
)

# Include module
include(${CMAKE_CURRENT_SOURCE_DIR}/external/cppscript/godot_cppscript.cmake)

# Get header files (.hpp only)
file(GLOB_RECURSE CPPSCRIPT_HEADERS src/*.hpp)

# Call function to configure your target
create_cppscript_target(
	# Name of header to be included to enable cppscript
	# (Prefer name unique to your project)
	HEADER_NAME
		cppscript.h

	# Header files to parse (.hpp only)
	HEADERS_LIST
		${CPPSCRIPT_HEADERS}

	# FULL PATH to C++ header files
	HEADERS_DIR
		${CMAKE_CURRENT_SOURCE_DIR}/src
	
	# Variable name for generated sources list
	OUTPUT_SOURCES
		GEN_SOURCES

	# Generate bindings to public methods automatically
	# or require GMETHOD() before methods
	AUTO_METHODS

	# Optional

	# C++ defines (TOOLS_ENABLED, DEBUG_METHODS etc.)
	# Enable, if you conditionally enable classes/members
	# based on definitions
	#
	 COMPILE_DEFS
	 	$<TARGET_PROPERTY:${LIBNAME},COMPILE_DEFINITIONS>

	# Include paths
	# (Try to avoid godot-cpp headers paths,
	# it slows parsing drastically)
	#
	# INCLUDE_PATHS
	# 	$<TARGET_PROPERTY:${LIBNAME},INCLUDE_DIRECTORIES>
)

# Add sources to your target
target_sources(
    ${LIBNAME}
	 PRIVATE ${GEN_SOURCES}
)

# Include headers path (if not done already)
target_include_directories(${LIBNAME} PRIVATE
	src
)
