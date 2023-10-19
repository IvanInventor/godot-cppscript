from cppscript import * #CppScriptBuilder



env = SConscript('godot-cpp/SConstruct')

env.Append(CPPPATH=['src/'])

sources = Glob("src/*.cpp")

# parsing only .hpp headers
# TODO: different ext. for script headers(?)/recursive search
scripts = Glob("src/*.hpp")

csb = Builder(
    action=generate_header,
    target='src/scripts.gen.h'
)

env.Append(BUILDERS={'CppScript' : csb})
#csb.generate_register_header()

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
