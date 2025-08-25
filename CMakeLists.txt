# Configuration based on godot-cpp/test/CMakeLists.txt
cmake_minimum_required(VERSION 3.13)
project(scripts LANGUAGES CXX)

add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/external/godot-cpp)

file(GLOB_RECURSE SOURCES CONFIGURE_DEPENDS src/*.c**)
file(GLOB_RECURSE HEADERS CONFIGURE_DEPENDS src/*.h**)

add_library(${PROJECT_NAME} SHARED EXCLUDE_FROM_ALL)
target_sources(
    ${PROJECT_NAME}
	 PRIVATE ${SOURCES} ${HEADERS}
)

# conditionally add doc data to compile output
if(GODOTCPP_TARGET MATCHES "editor|template_debug")
    find_package(Python3 3.4 REQUIRED)
    file(GLOB_RECURSE DOC_XML LIST_DIRECTORIES NO CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/doc_classes/*.xml")
    target_doc_sources( ${PROJECT_NAME} ${DOC_XML} )
endif()

set(OUTPUT_DIR "${CMAKE_CURRENT_SOURCE_DIR}/bin/")

# Link to godot-cpp target
target_link_libraries(${PROJECT_NAME} PRIVATE godot-cpp)

### Get useful properties from godot-cpp target
get_target_property(GODOTCPP_SUFFIX godot-cpp GODOTCPP_SUFFIX)

# gersemi: off
set_target_properties(
    ${PROJECT_NAME}
    PROPERTIES
        CXX_STANDARD 17
        CXX_EXTENSIONS OFF
        CXX_VISIBILITY_PRESET ${GODOTCPP_SYMBOL_VISIBILITY}

        POSITION_INDEPENDENT_CODE ON
        BUILD_RPATH_USE_ORIGIN ON

        # Try to ensure only static libraries are selected to be linked to.
        LINK_SEARCH_START_STATIC ON
        LINK_SEARCH_END_STATIC ON

        # NOTE: Wrapping the output variables inside a generator expression
        # prevents msvc generator from adding addition Config Directories
        LIBRARY_OUTPUT_DIRECTORY "$<1:${OUTPUT_DIR}>"
        RUNTIME_OUTPUT_DIRECTORY "$<1:${OUTPUT_DIR}>"
        PDB_OUTPUT_DIRECTORY     "$<1:${OUTPUT_DIR}>" #MSVC Only, ignored on other platforms

        PREFIX "lib"
		  OUTPUT_NAME "${PROJECT_NAME}${GODOTCPP_SUFFIX}"
        # TODO rename the file for both CMake and SCons

        # Some IDE's respect this property to logically group targets
        FOLDER "godot-cpp"
)
# gersemi: on

# CMAKE_SYSTEM_NAME refers to the target system
if(CMAKE_SYSTEM_NAME STREQUAL Darwin)
    set_target_properties(
        ${PROJECT_NAME}
        PROPERTIES SUFFIX "" OUTPUT_DIR "${OUTPUT_DIR}/libgdexample.macos.${GODOTCPP_TARGET}.framework"
    )
endif()

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
	 	$<TARGET_PROPERTY:${PROJECT_NAME},COMPILE_DEFINITIONS>

	# Include paths
	# (Try to avoid godot-cpp headers paths,
	# it slows parsing drastically)
	#
	# INCLUDE_PATHS
	# 	$<TARGET_PROPERTY:${PROJECT_NAME},INCLUDE_DIRECTORIES>
)

# Add sources to your target
target_sources(
    ${PROJECT_NAME}
	 PRIVATE ${GEN_SOURCES}
)

# Include headers path (if not done already)
target_include_directories(${PROJECT_NAME} PRIVATE
	src
)
