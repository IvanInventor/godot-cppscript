#!/usr/bin/env python3

import os, sys

path = sys.argv[1] if len(sys.argv) > 1 else 'master'

if not os.path.isdir(path):
    print(f'Prepare worktree with `git worktree add {path} master` first...')
    exit(1)

def replace(fstr, key_value):
    for key, value in key_value:
        fstr = fstr.replace(key, value)

    return fstr

def embed_py(var_name, body):
    fbody = body.replace("\\", "\\\\") 
    return f'{var_name} = """\n{fbody}\n"""\n'

def embed_cmake(var_name, body):
    fbody = body.replace('\\', '\\\\').replace('"', '\\"')
    return f'set({var_name} "{fbody}"\n)\n'

# .py templates
TEMPLATE_SCONS = open('template_scons.py').read()
TEMPLATE_CMAKE = open('template_cmake.py').read()

# cmake template
CMAKE_MODULE = open('godot_cppscript.cmake').read()

# script for configuring new project
PY_CONFIGURE_SCRIPT = open('configure_script.py').read()

# main module code
CPPSCRIPT_PY_MODULE = open('cppscript.py').read()

# files to embed
REGISTER_TYPES_CPP_IN = open('templates/register_types.cpp.in', 'r').read()
REGISTER_TYPES_H_IN = open('templates/register_types.h.in', 'r').read()
SCRIPTS_GDEXTENSION_IN = open('templates/scripts.gdextension.in', 'r').read()

CPPSCRIPT_DEFS_H = open('src/cppscript_defs.h').read()
CPPSCRIPT_BINDINGS_H = open('src/cppscript_bindings.h').read()

PY_CONFIGURE_SCRIPT = replace(PY_CONFIGURE_SCRIPT, [
            ('@PY_EMBED_TEMPLATE_FILES@',
            embed_py("REGISTER_TYPES_CPP_IN", REGISTER_TYPES_CPP_IN) + \
            '    ' + embed_py("REGISTER_TYPES_H_IN", REGISTER_TYPES_H_IN) + \
            '    ' + embed_py("SCRIPTS_GDEXTENSION_IN", SCRIPTS_GDEXTENSION_IN))

            ]
        )

open(os.path.join(path, 'godot_cppscript.py'), 'w').write(
    replace(TEMPLATE_SCONS, [
        ('@PY_CONFIGURE_SCRIPT@', 
            PY_CONFIGURE_SCRIPT),
        ('@PY_EMBED_SRC_FILES@',
            embed_py("CPPSCRIPT_DEFS_H", CPPSCRIPT_DEFS_H) + \
            embed_py("CPPSCRIPT_BINDINGS_H", CPPSCRIPT_BINDINGS_H)),
        ('@CPPSCRIPT_PY_MODULE@',
            CPPSCRIPT_PY_MODULE)
        ]
    )
)

CMAKE_EMBED_PY_SCRIPT = replace(TEMPLATE_CMAKE, [
    ('@CPPSCRIPT_PY_MODULE@',
        CPPSCRIPT_PY_MODULE)
    ]
)

open(os.path.join(path, 'godot_cppscript.cmake'), 'w').write(
    replace(CMAKE_MODULE, [
        ('@CMAKE_EMBED_CONFIGURE_SCRIPT@',
         embed_cmake('PY_CONFIGURE_SCRIPT', PY_CONFIGURE_SCRIPT.replace('\n    ', '\n')[4:])),
        ('@CMAKE_EMBED_SRC_FILES@',
            embed_cmake("CPPSCRIPT_DEFS_H", CPPSCRIPT_DEFS_H) + \
            embed_cmake("CPPSCRIPT_BINDINGS_H", CPPSCRIPT_BINDINGS_H) + \
            embed_cmake("CPPSCRIPT_EMBED_PY_SCRIPT", CMAKE_EMBED_PY_SCRIPT)),
        ]
    )
)
