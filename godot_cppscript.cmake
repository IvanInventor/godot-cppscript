cmake_minimum_required(VERSION 3.6)

find_package(Python3 3.4 REQUIRED)

if(CMAKE_SCRIPT_MODE_FILE)
    # Ran as configure script

@CMAKE_EMBED_CONFIGURE_SCRIPT@

	 # Pass args to python config script
	 math(EXPR ARGC "${CMAKE_ARGC} - 1")
	 foreach(i RANGE 3 ${ARGC})
		 list(APPEND ARGS "${CMAKE_ARGV${i}}")
	 endforeach()

    execute_process(
        COMMAND
            "${Python3_EXECUTABLE}"
				"-c"
				"${PY_CONFIGURE_SCRIPT}"
				${ARGS}
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    )


else()

@CMAKE_EMBED_SRC_FILES@

#TODO: script path is changed to generated one
set(CMAKE_CURRENT_FUNCTION_LIST_DIR ${CMAKE_CURRENT_LIST_DIR})

#TODO: make it work in parallel
function(create_cppscript_target TARGET_NAME HEADERS_LIST HEADER_NAME HEADERS_DIR GEN_DIR AUTO_METHODS COMPILE_DEFS INCLUDE_PATHS)
    #TODO: cmake_parse_args
	# Handle empty/NOTFOUND lists
	if(NOT INCLUDE_PATHS)
		set(INCLUDE_PATHS "")
	endif()
	if(NOT COMPILE_DEFS)
		set(COMPILE_DEFS "")
	endif()


	if(${AUTO_METHODS})
		set(AUTO_METHODS_STR "True")
	else()
		set(AUTO_METHODS_STR "False")
	endif()

    # Generate python script and headers
    set(GODOT_CPPSCRIPT_PY_SCRIPT_PATH "${CMAKE_CURRENT_BINARY_DIR}/cppscript.py")
    set(GODOT_CPPSCRIPT_DEFS_H_PATH "${HEADERS_DIR}/cppscript_defs.h")
    set(GODOT_CPPSCRIPT_BINDINGS_H_PATH "${HEADERS_DIR}/cppscript_bindings.h")

    file(WRITE "${GODOT_CPPSCRIPT_PY_SCRIPT_PATH}" "${CPPSCRIPT_EMBED_PY_SCRIPT}")
    file(WRITE "${GODOT_CPPSCRIPT_DEFS_H_PATH}" "${CPPSCRIPT_DEFS_H}")
    file(WRITE "${GODOT_CPPSCRIPT_BINDINGS_H_PATH}" "${CPPSCRIPT_BINDINGS_H}")
	foreach(PATH ${HEADERS_LIST})
		file(RELATIVE_PATH PATH "${HEADERS_DIR}" "${PATH}")
		string(REGEX REPLACE "\.[^./\\]+$" ".gen.cpp" relative_path "${PATH}")
		list(APPEND SOURCES_LIST "${GEN_DIR}/${relative_path}")
	endforeach()

	add_custom_command(
		OUTPUT
			${HEADERS_DIR}/${HEADER_NAME}
			${HEADERS_DIR}/scripts.gen.h
			${HEADERS_DIR}/properties.gen.h
			${SOURCES_LIST}

		COMMAND
			${Python3_EXECUTABLE} "${CMAKE_CURRENT_FUNCTION_LIST_DIR}/cppscript_bindings.py"
			"--header-name" "${HEADER_NAME}"
			"--header-dir" "${HEADERS_DIR}"
			"--gen-dir" "${GEN_DIR}"
			"--auto-methods" "${AUTO_METHODS_STR}"
			"--definitions" ${COMPILE_DEFS}
			"--include-paths" ${CMAKE_CURRENT_FUNCTION_LIST_DIR}/src ${HEADERS_DIR} ${INCLUDE_PATHS}
			"--"
			${HEADERS_LIST}

		DEPENDS ${HEADERS_LIST}
		WORKING_DIRECTORY ${CMAKE_CURRENT_FUNCTION_LIST_DIR}
		VERBATIM
		COMMAND_EXPAND_LISTS
		COMMENT "Parsing header files..."
	)

	target_sources(${TARGET_NAME} PRIVATE ${SOURCES_LIST})
	target_include_directories(${TARGET_NAME} PUBLIC ${CMAKE_CURRENT_FUNCTION_LIST_DIR}/src ${HEADERS_DIR})
endfunction()


endif()
