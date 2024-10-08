# THIS FILE IS AUTO-GENERATED
# See `https://github.com/IvanInventor/godot-cppscript/tree/next` for proper source
cmake_minimum_required(VERSION 3.12.4)

find_package(Python3 3.10 REQUIRED)

if(CMAKE_SCRIPT_MODE_FILE)
    # Ran as configure script

@CMAKE_EMBED_CONFIGURE_SCRIPT@

	# Pass args to python config script
	math(EXPR ARGC "${CMAKE_ARGC} - 1")
	foreach(i RANGE 3 ${ARGC})
		list(APPEND ARGS "${CMAKE_ARGV${i}}")
	endforeach()

	set(SCRIPT_PATH "${CMAKE_CURRENT_SOURCE_DIR}/.configure_script.py.tmp")
	file(WRITE ${SCRIPT_PATH} "${PY_CONFIGURE_SCRIPT}")
   execute_process(
      COMMAND
         "${Python3_EXECUTABLE}"
			"${SCRIPT_PATH}"
			${ARGS}
      WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
   )
	file(REMOVE ${SCRIPT_PATH})

else()

@CMAKE_EMBED_SRC_FILES@

set(EMBED_CPPSCRIPT_H "#ifndef @H_GUARD@
#define @H_GUARD@
#include <cppscript_defs.h>
#include \"properties.gen.h\"
#endif // @H_GUARD@
"
)

#TODO: make it work in parallel
function(create_cppscript_target)
	set(options AUTO_METHODS)
	set(oneValueArgs HEADER_NAME HEADERS_DIR GEN_DIR OUTPUT_SOURCES)
	set(multiValueArgs HEADERS_LIST COMPILE_DEFS INCLUDE_PATHS)
	cmake_parse_arguments(CPPS "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

	# Handle required args and empty/NOTFOUND lists
	if(NOT CPPS_HEADER_NAME)
		message(FATAL_ERROR "Header name is required argument (for example: `HEADER_NAME project_name.h`)")
	endif()

	if(NOT CPPS_HEADERS_DIR)
		message(FATAL_ERROR "Headers directory is required argument (for example: `HEADERS_DIR \${CMAKE_CURRENT_SOURCE_DIR}/include`)")
	endif()
	
	if(NOT CPPS_OUTPUT_SOURCES)
		message(FATAL_ERROR "Output sources is required argument (for example: `OUTPUT_SOURCES GEN_SOURCES`)")
	endif()

	if(NOT CPPS_GEN_DIR)
		set(CPPS_GEN_DIR "${CMAKE_CURRENT_BINARY_DIR}/.cppscript.gen")
	endif()
	
	if(NOT CPPS_HEADERS_LIST)
		set(CPPS_HEADERS_LIST "")
	endif()
	
	if(NOT CPPS_COMPILE_DEFS)
		set(CPPS_COMPILE_DEFS "")
	endif()
	
	if(NOT CPPS_INCLUDE_PATHS)
		set(CPPS_INCLUDE_PATHS "")
	endif()

	if(CPPS_AUTO_METHODS)
		set(AUTO_METHODS_STR "True")
	else()
		set(AUTO_METHODS_STR "False")
	endif()

    # Generate python script and headers
    set(GODOT_CPPSCRIPT_PY_SCRIPT_PATH "${CMAKE_CURRENT_BINARY_DIR}/cppscript.py")
	 set(GODOT_CPPSCRIPT_DEFS_H_PATH "${CPPS_HEADERS_DIR}/cppscript_defs.h")
    set(GODOT_CPPSCRIPT_BINDINGS_H_PATH "${CPPS_HEADERS_DIR}/cppscript_bindings.h")
	 set(GODOT_CPPSCRIPT_H_PATH "${CPPS_HEADERS_DIR}/${CPPS_HEADER_NAME}")

    file(WRITE "${GODOT_CPPSCRIPT_PY_SCRIPT_PATH}" "${CPPSCRIPT_EMBED_PY_SCRIPT}")
    file(WRITE "${GODOT_CPPSCRIPT_DEFS_H_PATH}" "${CPPSCRIPT_DEFS_H}")
    file(WRITE "${GODOT_CPPSCRIPT_BINDINGS_H_PATH}" "${CPPSCRIPT_BINDINGS_H}")

	 string(TOUPPER "${CPPS_HEADER_NAME}" H_GUARD_STR)
	 string(REPLACE "." "_" H_GUARD_STR "${H_GUARD_STR}")
	 string(REPLACE "@H_GUARD@" "${H_GUARD_STR}" EMBED_CPPSCRIPT_H_FORMATTED "${EMBED_CPPSCRIPT_H}") 
	 file(WRITE "${GODOT_CPPSCRIPT_H_PATH}" "${EMBED_CPPSCRIPT_H_FORMATTED}")

	foreach(PATH ${CPPS_HEADERS_LIST})
		file(RELATIVE_PATH PATH "${CPPS_HEADERS_DIR}" "${PATH}")
		string(REGEX REPLACE "\.[^./\\]+$" ".gen.cpp" relative_path "${PATH}")
		list(APPEND SOURCES_LIST "${CPPS_GEN_DIR}/${relative_path}")
	endforeach()

	add_custom_command(
		OUTPUT
			${CPPS_HEADERS_DIR}/${CPPS_HEADER_NAME}
			${CPPS_HEADERS_DIR}/scripts.gen.h
			${CPPS_HEADERS_DIR}/properties.gen.h
			${SOURCES_LIST}

		COMMAND
			${Python3_EXECUTABLE} "${GODOT_CPPSCRIPT_PY_SCRIPT_PATH}"
				"--header-name" "${CPPS_HEADER_NAME}"
				"--header-dir" "${CPPS_HEADERS_DIR}"
				"--gen-dir" "${CPPS_GEN_DIR}"
				"--auto-methods" "${AUTO_METHODS_STR}"
				"--definitions" ${CPPS_COMPILE_DEFS}
				"--include-paths" ${CPPS_HEADERS_DIR} ${CPPS_INCLUDE_PATHS}
				"--"
				${CPPS_HEADERS_LIST}

		DEPENDS ${CPPS_HEADERS_LIST}
		WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
		VERBATIM
		COMMAND_EXPAND_LISTS
		COMMENT "Parsing header files..."
	)
	set(${CPPS_OUTPUT_SOURCES} "${SOURCES_LIST}" PARENT_SCOPE)
endfunction()

endif()
