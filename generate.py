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
    return f'{var_name} = """\n{body.replace("\\", "\\\\")}\n"""\n'

def embed_cmake(var_name, body):
    fbody = body.replace('\\', '\\\\').replace('"', '\\"')
    return f'set({var_name} "{fbody}"\n)\n'

PY_TEMPLATE = open('godot_cppscript.py').read()
CMAKE_TEMPLATE = open('godot_cppscript.cmake').read()
CPPSCRIPT_PY_MODULE = open('cppscript.py').read()

REGISTER_TYPES_CPP_IN = open('templates/register_types.cpp.in', 'r').read()
REGISTER_TYPES_H_IN = open('templates/register_types.h.in', 'r').read()
SCRIPTS_GDEXTENSION_IN = open('templates/scripts.gdextension.in', 'r').read()

CPPSCRIPT_DEFS_H = open('src/cppscript_defs.h').read()
CPPSCRIPT_BINDINGS_H = open('src/cppscript_bindings.h').read()

open(os.path.join(path, 'godot_cppscript.py'), 'w').write(
    replace(PY_TEMPLATE, [
        ('@PY_EMBED_TEMPLATE_FILES@',
            '    ' + embed_py("REGISTER_TYPES_CPP_IN", REGISTER_TYPES_CPP_IN) + \
            '    ' + embed_py("REGISTER_TYPES_H_IN", REGISTER_TYPES_H_IN) + \
            '    ' + embed_py("SCRIPTS_GDEXTENSION_IN", SCRIPTS_GDEXTENSION_IN)),
        ('@PY_EMBED_SRC_FILES@',
            embed_py("CPPSCRIPT_DEFS_H", CPPSCRIPT_DEFS_H) + \
            embed_py("CPPSCRIPT_BINDINGS_H", CPPSCRIPT_BINDINGS_H)),
        ('@CPPSCRIPT_PY_MODULE@',
            CPPSCRIPT_PY_MODULE)
        ]
    )
)

CMAKE_EMBED_PY_SCRIPT = replace(PY_TEMPLATE, [
    ('@PY_EMBED_TEMPLATE_FILES@',
        '    ' + embed_py("REGISTER_TYPES_CPP_IN", REGISTER_TYPES_CPP_IN) + \
        '    ' + embed_py("REGISTER_TYPES_H_IN", REGISTER_TYPES_H_IN) + \
        '    ' + embed_py("SCRIPTS_GDEXTENSION_IN", SCRIPTS_GDEXTENSION_IN)),
    ('@PY_EMBED_SRC_FILES@',
        ''),
    ('@CPPSCRIPT_PY_MODULE@',
        CPPSCRIPT_PY_MODULE)
    ]
)

open(os.path.join(path, 'godot_cppscript.cmake'), 'w').write(
    replace(CMAKE_TEMPLATE, [
        ('@CMAKE_EMBED_SRC_FILES@',
            embed_cmake("CPPSCRIPT_DEFS_H", CPPSCRIPT_DEFS_H) + \
            embed_cmake("CPPSCRIPT_BINDINGS_H", CPPSCRIPT_BINDINGS_H) + \
            embed_cmake("CPPSCRIPT_EMBED_PY_SCRIPT", CMAKE_EMBED_PY_SCRIPT)),
        ]
    )
)
