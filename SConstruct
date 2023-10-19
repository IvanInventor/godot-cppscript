from cppscript import CppScriptBuilder



env = SConscript('godot-cpp/SConstruct')

csb = CppScriptBuilder(env)
csb.generate_register_header()

library_name = 'libscripts' + env['suffix'] + env['LIBSUFFIX']

if env["platform"] == "macos":
    library = env.SharedLibrary(
        "bin/libscripts.{}.{}.framework/libgdexample.{}.{}".format(
            env["platform"], env["target"], env["platform"], env["target"]
        ),
        source=csb.sources,
    )
else:
    library = env.SharedLibrary(
        "bin/libscripts{}{}".format(env["suffix"], env["SHLIBSUFFIX"]),
        source=csb.sources,
    )

env.Ignore(library, csb.src + 'scripts.gen.h')
Default(library)
