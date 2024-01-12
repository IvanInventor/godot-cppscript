# TEMPORARILY works only on top of my godot-cpp Cmake rewrite
cmake_minimum_required(VERSION 3.24)
project(scripts)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake/")
include(godot-cppscript)

add_subdirectory(godot-cpp)

# Get Sources
file(GLOB_RECURSE SOURCES ../src/*.c**)

###############################
set(INCLUDE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../src)
set(GEN_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../.gen)
set(GEN_HEADER ${CMAKE_CURRENT_SOURCE_DIR}/../src/scripts.gen.h)

file(GLOB_RECURSE CPPSCRIPT_HEADERS ../src/*.hpp)

create_cppscript_target(
	cppscript.h
	${CMAKE_CURRENT_SOURCE_DIR}
	${INCLUDE_DIR}
	${GEN_DIR}
	${GEN_HEADER}
	ON
	CPPSCRIPT_MY_SOURCES
)

###############################
# Define our godot-cpp library
message("MY_SOURCES=${CPPSCRIPT_MY_SOURCES}")
add_library(${PROJECT_NAME} SHARED
	${SOURCES}
	${CPPSCRIPT_MY_SOURCES}
	${GEN_HEADER}
	${CPPSCRIPT_HEADERS}
	src/register_types.cpp
)

#add_dependencies(${PROJECT_NAME} cppscript-target)
target_include_directories(${PROJECT_NAME} PRIVATE ../src src/)

target_link_libraries(${PROJECT_NAME} PUBLIC godot-cpp)

get_directory_property(GODOT_C_FLAGS DIRECTORY godot-cpp DEFINITION GODOT_C_FLAGS)
get_directory_property(GODOT_CXX_FLAGS DIRECTORY godot-cpp DEFINITION GODOT_CXX_FLAGS)
target_compile_options(${PROJECT_NAME} PRIVATE
	${GODOT_C_FLAGS}
	${GODOT_CXX_FLAGS}
)

get_directory_property(GODOT_LINK_FLAGS DIRECTORY godot-cpp DEFINITION GODOT_LINK_FLAGS)
target_link_options(${PROJECT_NAME} PRIVATE ${GODOT_LINK_FLAGS}) # -Wl,--as-needed -nostdlib++)


get_directory_property(LIBRARY_SUFFIX DIRECTORY godot-cpp DEFINITION LIBRARY_SUFFIX)
set_target_properties(${PROJECT_NAME}
	PROPERTIES
		ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/../bin"
		LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/../bin"
		RUNTIME_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/../bin"
	
		OUTPUT_NAME "${PROJECT_NAME}${LIBRARY_SUFFIX}"
)

