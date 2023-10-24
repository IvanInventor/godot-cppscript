from cppscript import *
import os

SRC_DIR = '../src'

env = SConscript('godot-cpp/SConstruct')

env.Append(CPPPATH=['src/', SRC_DIR])
env['src'] = SRC_DIR

sources = Glob(os.path.join(SRC_DIR, '*.cpp')) + Glob('src/register_types.cpp')

# parsing only .hpp headers
# TODO: different ext. for script headers(?)/recursive search
scripts = Glob(os.path.join(SRC_DIR, '*.hpp'))

csb = Builder(
    action=generate_header,
    emitter=generate_header_emitter,
)

env.Append(BUILDERS={'CppScript' : csb})

library_name = 'libscripts' + env['suffix'] + env['LIBSUFFIX']

cpp = env.CppScript(scripts)
if env["platform"] == "macos":
    library = env.SharedLibrary(
        "bin/libscripts.{}.{}.framework/libgdexample.{}.{}".format(
            env["platform"], env["target"], env["platform"], env["target"]
        ),
        source=sources,
    )
else:
    library = env.SharedLibrary(
        "bin/libscripts{}{}".format(env["suffix"], env["SHLIBSUFFIX"]),
        source=sources,
    )

env.Ignore(library, 'src/scripts.gen.h')
env.Depends(sources, cpp)
Default(library)
