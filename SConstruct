from cppscript import *
import os

SRC_DIR = '../src'
library_name = 'scripts'

env = SConscript('godot-cpp/SConstruct')

env.Append(CPPPATH=[SRC_DIR, 'src'])
env['src'] = SRC_DIR
env['gen_header'] = 'src/scripts.gen.h'

sources = GlobRecursive(SRC_DIR, '*.cpp') + Glob('src/register_types.cpp')
scripts = GlobRecursive(SRC_DIR, '*.hpp')

csb = Builder(
    action=generate_header,
    emitter=generate_header_emitter,
)

env.Append(BUILDERS={'CppScript' : csb})

cpp = env.CppScript(scripts)
if env["platform"] == "macos":
    library = env.SharedLibrary(
        "../bin/lib{}.{}.{}.framework/lib{}.{}.{}".format(
            library_name, env["platform"], env["target"], library_name, env["platform"], env["target"]
        ),
        source=sources,
    )
else:
    library = env.SharedLibrary(
        "../bin/lib{}{}{}".format(library_name, env["suffix"], env["SHLIBSUFFIX"]),
        source=sources,
    )

env.Ignore(library, env['gen_header'])
env.Depends(sources, cpp)
Default(library)
