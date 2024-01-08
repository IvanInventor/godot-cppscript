from cppscript import GlobRecursive, generate_header_scons, generate_header_emitter
import os

SRC_DIR = '../src'
library_name = 'scripts'

env = SConscript('godot-cpp/SConstruct').Clone()

sources = GlobRecursive(SRC_DIR, '*.cpp') + [env.File('src/register_types.cpp')]
scripts = GlobRecursive(SRC_DIR, '*.hpp')

env.Append(CPPPATH=[SRC_DIR, 'src'])
								# CppScript config
env['src'] = SRC_DIR						# Path to C++ source files
env['gen_dir'] = "../.gen"					# Path for generated object files
env['defs_file'] = os.path.join(SRC_DIR, 'defs.json')		# Path to generated bindings
env['gen_header'] = os.path.join(SRC_DIR, 'scripts.gen.h')	# Path to generated header
env['auto_methods'] = True					# Generate bindings to public methods automatically
								# Or require GMETHOD() before methods
env.Append(BUILDERS={'CppScript' : Builder(
    action=generate_header_scons,
    emitter=generate_header_emitter)})

generated = env.CppScript(scripts)
header, *bindings = generated

env.Precious(generated)

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

env.Depends(library[0].sources, generated)

Default(library)
