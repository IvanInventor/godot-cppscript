find_package(Python3 3.4 REQUIRED)

#TODO: make it work in parallel
function(create_cppscript_target HEADER_NAME GODOT_CPPSCRIPT_DIR HEADERS_DIR GEN_DIR GEN_HEADER AUTO_METHODS CPPSCRIPT_SOURCES)
	if(${AUTO_METHODS})
		set(AUTO_METHODS_STR "True")
	else()
		set(AUTO_METHODS_STR "False")
	endif()

	file(GLOB_RECURSE HEADERS_LIST RELATIVE ${HEADERS_DIR} ${HEADERS_DIR}/*.hpp)
	
	foreach(PATH ${HEADERS_LIST})
		string(REGEX REPLACE "\.hpp$" ".gen.cpp" relative_path "${PATH}")
		list(APPEND SOURCES_LIST ${GEN_DIR}/${relative_path})
	endforeach()
	set(${CPPSCRIPT_SOURCES} ${SOURCES_LIST} PARENT_SCOPE)

	add_custom_command(OUTPUT ${GEN_HEADER} ${SOURCES_LIST}
		COMMAND ${Python3_EXECUTABLE} "${GODOT_CPPSCRIPT_DIR}/cppscript_bindings.py"
		"--header-name" "${HEADER_NAME}"
		"--src" "${HEADERS_DIR}"
		"--gen-dir" "${GEN_DIR}"
		"--gen-header" "${GEN_HEADER}"
		"--auto-methods" "${AUTO_METHODS_STR}"
		${CPPSCRIPT_HEADERS}

		DEPENDS ${CPPSCRIPT_HEADERS}
		WORKING_DIRECTORY ${GODOT_CPPSCRIPT_DIR}
		VERBATIM
		COMMENT "Parsing header files..."
	)
	
	#add_custom_target(${TARGET_NAME} DEPENDS ${GEN_HEADER} ${SOURCES_LIST})
	#foreach(file ${SOURCES_LIST})
	#	file(WRITE ${file} "")
#	endforeach()
	file(REMOVE ${GEN_DIR}/defs.json)
endfunction()

