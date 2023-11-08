from cppscript import GlobRecursive, generate_header, generate_header_emitter
import os

SRC_DIR = '../src'
library_name = 'scripts'

env = SConscript('godot-cpp/SConstruct').Clone()

env.Append(CPPPATH=[SRC_DIR, 'src'])		# CppScript config
env['src'] = SRC_DIR				# Path to C++ source files
env['defs_file'] = '../src/defs.json'		# Path to generated bindings
env['gen_header'] = '../src/scripts.gen.h'	# Path to generated header
env['auto_methods'] = True			# Generate bindings to public methods automatically
						# Or require GMETHOD() before methods

sources = GlobRecursive(SRC_DIR, '*.cpp') + [env.File('src/register_types.cpp')]
scripts = GlobRecursive(SRC_DIR, '*.hpp')

csb = Builder(
    action=generate_header,
    emitter=generate_header_emitter,
)

env.Append(BUILDERS={'CppScript' : csb})

header, *bindings = env.CppScript(scripts)
env.Precious(bindings)


if env["platform"] == "macos":
    library = env.SharedLibrary(
        "../bin/lib{}.{}.{}.framework/lib{}.{}.{}".format(
            library_name, env["platform"], env["target"], library_name, env["platform"], env["target"]
        ),
	source=sources + bindings,
    )
else:
    library = env.SharedLibrary(
        "../bin/lib{}{}{}".format(library_name, env["suffix"], env["SHLIBSUFFIX"]),
        source=sources + bindings,
    )

env.Depends(library[0].sources, bindings)
Default(library)
