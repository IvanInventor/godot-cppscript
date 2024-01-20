find_package(Python3 3.4 REQUIRED)

set(CPPSCRIPT_DIR ${CMAKE_CURRENT_LIST_DIR})

#TODO: make it work in parallel
function(create_cppscript_target TARGET_NAME HEADERS_LIST HEADER_NAME HEADERS_DIR GEN_DIR AUTO_METHODS COMPILE_DEFS INCLUDE_PATHS)
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
			${Python3_EXECUTABLE} "${CPPSCRIPT_DIR}/cppscript_bindings.py"
			"--header-name" "${HEADER_NAME}"
			"--header-dir" "${HEADERS_DIR}"
			"--gen-dir" "${GEN_DIR}"
			"--auto-methods" "${AUTO_METHODS_STR}"
			"--definitions" ${COMPILE_DEFS}
			"--include-paths" ${CPPSCRIPT_DIR}/src ${HEADERS_DIR} ${INCLUDE_PATHS}
			"--"
			${HEADERS_LIST}

		DEPENDS ${HEADERS_LIST}
		WORKING_DIRECTORY ${CPPSCRIPT_DIR}
		VERBATIM
		COMMAND_EXPAND_LISTS
		COMMENT "Parsing header files..."
	)

	target_sources(${TARGET_NAME} PRIVATE ${SOURCES_LIST})
	target_include_directories(${TARGET_NAME} PUBLIC ${CPPSCRIPT_DIR}/src ${HEADERS_DIR})
endfunction()

