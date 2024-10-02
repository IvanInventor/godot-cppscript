import os, sys
from external.cppscript.godot_cppscript import create_cppscript_target, GlobRecursive

# Customize this values depending on your project
library_name = 'scripts'
SRC_DIR = 'src'
GEN_DIR = '.gen'

env = SConscript('external/godot-cpp/SConstruct').Clone()

sources = GlobRecursive(SRC_DIR, '*.cpp')

env.Append(CXXFLAGS='-fdiagnostics-color=always')

###############################
# godot-cppscript creation

# Get header files (.hpp only)
scripts = GlobRecursive(SRC_DIR, '*.hpp')

# Create target, returns generated .cpp files list
generated = create_cppscript_target(
		env,		# SCons env, env.Clone() for different projects
		scripts,	# Header files to parse

		# CppScript config
		{
		# Name of header to be included to enable cppscript
		# (Prefer name unique to your project)
		'header_name' : 'cppscript.h',

		# Path to C++ header files
		'header_dir' : SRC_DIR,

		# Path to generated object files
		'gen_dir' : GEN_DIR,

		# Generate bindings to public methods automatically
		# or require GMETHOD() before methods
		'auto_methods' : True,

		# Optional

		## C++ defines (TOOLS_ENABLED, DEBUG_METHODS etc.)
		## Enable, if you conditionally enable classes/members
		## based on definitions
		'compile_defs' : env['CPPDEFINES'],
		#
		## Include paths
		## (Try to avoid godot-cpp headers paths,
		## it slows parsing drastically)
		#'include_paths' : env['CPPPATH']
		}
)

# Include headers path (if not done already)
env.Append(CPPPATH=SRC_DIR)
###############################

if env["platform"] == "macos":
    library = env.SharedLibrary(
	"bin/lib{}.{}.{}.framework/lib{}.{}.{}".format(
	library_name, env["platform"], env["target"], library_name, env["platform"], env["target"]
	),
	source=sources + generated, # Add generated source files to target
    )
else:
    library = env.SharedLibrary(
	"bin/lib{}{}{}".format(library_name, env["suffix"], env["SHLIBSUFFIX"]),
	source=sources + generated, # Add generated source files to target
    )

###############################
# Rebuild after headers change
env.Depends(library[0].sources, generated)

###############################

Default(library)
