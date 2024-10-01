# TEMPORARILY works only on top of my godot-cpp Cmake rewrite
cmake_minimum_required(VERSION 3.13)
project(scripts LANGUAGES CXX)

set(CMAKE_CONFIGURATION_TYPES "Debug;Release;RelWithDebInfo;MinSizeRel")

add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/external/godot-cpp)

# Get Sources
file(GLOB_RECURSE SOURCES CONFIGURE_DEPENDS src/*.c**)
file(GLOB_RECURSE HEADERS CONFIGURE_DEPENDS src/*.h**)

godot_clear_default_flags()

get_target_property(LIBRARY_SUFFIX godot-cpp LIBRARY_SUFFIX)

if("${GODOT_TARGET}" STREQUAL "editor" OR "${GODOT_TARGET}" STREQUAL "template_debug")
	set(DOC_GEN_PATH "${CMAKE_CURRENT_SOURCE_DIR}/src/gen/doc_data.gen.cpp")
	file(GLOB_RECURSE DOC_FILES CONFIGURE_DEPENDS doc_classes/*.xml)

	godot_make_doc(
		DESTINATION ${DOC_GEN_PATH}
		SOURCES ${DOC_FILES}
		COMPRESSION Z_BEST_COMPRESSION
	)
	list(APPEND SOURCES ${DOC_GEN_PATH})
endif()

# Define our godot-cpp library
if("${GODOT_PLATFORM}" STREQUAL "web")
	# wasm libraries loaded with dlopen() are created like this in cmake
	add_executable(${PROJECT_NAME} ${SOURCES} ${HEADERS})
	set_target_properties(${PROJECT_NAME}
		PROPERTIES
			SUFFIX ".wasm"
			OUTPUT_NAME "${PROJECT_NAME}${LIBRARY_SUFFIX}"
	)
elseif("${GODOT_PLATFORM}" STREQUAL "macos")
	add_library(${PROJECT_NAME} SHARED ${SOURCES} ${HEADERS})
	set(OUTPUT_NAME "lib${PROJECT_NAME}${LIBRARY_SUFFIX}")
	set_target_properties(${PROJECT_NAME} PROPERTIES
		FRAMEWORK TRUE
		MACOSX_FRAMEWORK_IDENTIFIER "org.godotengine.lib${PROJECT_NAME}"
		MACOSX_BUNDLE_BUNDLE_NAME "lib${PROJECT_NAME}${LIBRARY_SUFFIX}"
		MACOSX_BUNDLE_SHORT_VERSION_STRING "1.0.0"
		MACOS_BUNDLE_BUNDLE_VERSION "1.0.0"

		OUTPUT_NAME "${OUTPUT_NAME}"
	)

	# Workaround of 'bin/***.framework/Resources' existing in godot-cpp repo by default'
	set(RESOURCES_DIR "${CMAKE_CURRENT_SOURCE_DIR}/project/bin/${OUTPUT_NAME}.framework/Resources")
	if(IS_DIRECTORY ${RESOURCES_DIR} AND NOT IS_SYMLINK ${RESOURCES_DIR})
		message(STATUS "Removing '${RESOURCES_DIR}' to create symlink ...")
		file(REMOVE_RECURSE ${RESOURCES_DIR})
	endif()

# TODO: IOS configuration
#elseif("${GODOT_PLATFORM}" STREQUAL "ios")
else()
	add_library(${PROJECT_NAME} SHARED ${SOURCES} ${HEADERS})
	set_target_properties(${PROJECT_NAME} PROPERTIES
		OUTPUT_NAME "${PROJECT_NAME}${LIBRARY_SUFFIX}"
)
endif()

target_link_libraries(${PROJECT_NAME} PUBLIC godot-cpp)

get_target_property(GODOT_C_FLAGS godot-cpp GODOT_C_FLAGS)
get_target_property(GODOT_CXX_FLAGS godot-cpp GODOT_CXX_FLAGS)
get_target_property(GODOT_COMPILE_WARNING_FLAGS godot-cpp GODOT_COMPILE_WARNING_FLAGS)
target_compile_options(${PROJECT_NAME} PRIVATE
	${GODOT_C_FLAGS}
	${GODOT_CXX_FLAGS}
	${GODOT_COMPILE_WARNING_FLAGS}
)

get_target_property(GODOT_LINK_FLAGS godot-cpp GODOT_LINK_FLAGS)
target_link_options(${PROJECT_NAME} PRIVATE ${GODOT_LINK_FLAGS})


get_target_property(LIBRARY_SUFFIX godot-cpp LIBRARY_SUFFIX)
set_target_properties(${PROJECT_NAME}
	PROPERTIES
		PREFIX "lib"
		LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/bin"
		LIBRARY_OUTPUT_DIRECTORY_DEBUG "${CMAKE_CURRENT_SOURCE_DIR}/bin"
		LIBRARY_OUTPUT_DIRECTORY_RELEASE "${CMAKE_CURRENT_SOURCE_DIR}/bin"
		LIBRARY_OUTPUT_DIRECTORY_RELWITHDEBINFO "${CMAKE_CURRENT_SOURCE_DIR}/bin"
		LIBRARY_OUTPUT_DIRECTORY_MINSIZEREL "${CMAKE_CURRENT_SOURCE_DIR}/bin"
		RUNTIME_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/bin"
		RUNTIME_OUTPUT_DIRECTORY_DEBUG "${CMAKE_CURRENT_SOURCE_DIR}/bin"
		RUNTIME_OUTPUT_DIRECTORY_RELEASE "${CMAKE_CURRENT_SOURCE_DIR}/bin"
		RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO "${CMAKE_CURRENT_SOURCE_DIR}/bin"
		RUNTIME_OUTPUT_DIRECTORY_MINSIZEREL "${CMAKE_CURRENT_SOURCE_DIR}/bin"
)

if(${GODOT_WARNING_AS_ERROR})
	set_warning_as_error(${PROJECT_NAME})
endif()

###############################
# godot-cppscript creation

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
# Add sources 
target_sources(${PROJECT_NAME} PRIVATE ${GEN_SOURCES})
# Include headers path (if not already done)
target_include_directories(${PROJECT_NAME} PRIVATE
	src
)
###############################

