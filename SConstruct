#!/usr/bin/env python
import os
import sys
import glob

from methods import print_error

from external.cppscript.godot_cppscript import create_cppscript_target

libname = "scripts"
projectdir = "project"

# Customize this values depending on your project
SRC_DIR = 'src'
GEN_DIR = '.gen'

localEnv = Environment(tools=["default"], PLATFORM="")

# Build profiles can be used to decrease compile times.
# You can either specify "disabled_classes", OR
# explicitly specify "enabled_classes" which disables all other classes.
# Modify the example file as needed and uncomment the line below or
# manually specify the build_profile parameter when running SCons.

# localEnv["build_profile"] = "build_profile.json"

customs = ["custom.py"]
customs = [os.path.abspath(path) for path in customs]

opts = Variables(customs, ARGUMENTS)
opts.Update(localEnv)

Help(opts.GenerateHelpText(localEnv))

env = localEnv.Clone()

if not (os.path.isdir("external/godot-cpp") and os.listdir("external/godot-cpp")):
    print_error("""godot-cpp is not available within this folder, as Git submodules haven't been initialized.
Run the following command to download godot-cpp:

    git submodule update --init --recursive""")
    sys.exit(1)

env = SConscript("external/godot-cpp/SConstruct", {"env": env, "customs": customs})

env.Append(CPPPATH=["src/"])
sources = Glob("src/*.cpp")

if env["target"] in ["editor", "template_debug"]:
    try:
        doc_data = env.GodotCPPDocData("src/gen/doc_data.gen.cpp", source=Glob("doc_classes/*.xml"))
        sources.append(doc_data)
    except AttributeError:
        print("Not including class reference as we're targeting a pre-4.3 baseline.")

# .dev doesn't inhibit compatibility, so we don't need to key it.
# .universal just means "compatible with all relevant arches" so we don't need to key it.
suffix = env['suffix'].replace(".dev", "").replace(".universal", "")

lib_filename = "{}{}{}{}".format(env.subst('$SHLIBPREFIX'), libname, suffix, env.subst('$SHLIBSUFFIX'))

###############################
# godot-cppscript creation

# Get header files (.hpp only)
scripts = glob.glob(f'{SRC_DIR}/**/*.hpp', recursive=True)

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
###############################

library = env.SharedLibrary(
    ".bin/{}/{}".format(env['platform'], lib_filename),
    #source=sources,
	source=sources + generated, # Add generated source files to target
)

###############################
# Rebuild after headers change
env.Depends(library[0].sources, generated)

###############################

copy = env.Install("bin/{}/".format(env["platform"]), library)

default_args = [library, copy]
Default(*default_args)
