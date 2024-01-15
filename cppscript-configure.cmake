cmake_minimum_required(VERSION 3.6)

message("0=${CMAKE_ARGV0}")
message("1=${CMAKE_ARGV1}")
message("2=${CMAKE_ARGV2}")
message("3=${CMAKE_ARGV3}")
message("4=${CMAKE_ARGV4}")
message("5=${CMAKE_ARGV5}")
message("${LIBRARY_NAME_FULL}")

set(LIBRARY_NAME_FULL "${CMAKE_ARGV3}")
set(SRC_DIR "${CMAKE_ARGV4}")
set(PROJECT_DIR "${CMAKE_ARGV5}")

set(REFERENCE_STR "Usage:\n\tcmake -P cppscript/cppscript-configure.cmake <library_name> <src_dir> <project_dir>")
if("${LIBRARY_NAME_FULL}" STREQUAL "")
	message(FATAL_ERROR "No library_name argument.\n${REFERENCE_STR}")
elseif("${SRC_DIR}" STREQUAL "")
	message(FATAL_ERROR "No source_dir argument.\n${REFERENCE_STR}")
elseif("${LIBRARY_NAME_FULL}" STREQUAL "")
	message(FATAL_ERROR "No project_dir argument.\n${REFERENCE_STR}")
endif()


string(REPLACE "-" "_" LIBRARY_NAME "${LIBRARY_NAME_FULL}")

configure_file(
	${CMAKE_CURRENT_LIST_DIR}/templates/scripts.gdextension.in
	${PROJECT_DIR}/${LIBRARY_NAME_FULL}.gdextension
)

configure_file(
	${CMAKE_CURRENT_LIST_DIR}/templates/register_types.h.in
	${SRC_DIR}/register_types.h
)

configure_file(
	${CMAKE_CURRENT_LIST_DIR}/templates/register_types.cpp.in
	${SRC_DIR}/register_types.cpp
)

