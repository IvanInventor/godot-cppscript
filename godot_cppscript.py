#!/usr/bin/env python3

import sys

if __name__ == '__main__' and len(sys.argv) > 2 and sys[1] == 'configure':
    # Ran as configure script
    import os

@PY_EMBED_TEMPLATE_FILES@

    try:
        library_name = sys.argv[2].replace('-', '_')
        cpp_path = sys.argv[3]
        h_path = sys.argv[4]
        gdext_path = sys.argv[5]
    except:
        ABOUT = \
"""
ERROR: Not enough arguments.
Needed arguments (<argument> - example):

    <library_name>              (`my_library_name`)
    <cpp_file_path>             (`src/register_types.cpp`)
    <header_file_path>          (`include/register_types.h`)
    <gdextension_file_path>     (`project/my_library.gdextension`)
"""
        print(ABOUT, file=sys.stderr)
        exit(1)

    print(f"Configuring '{gdext_path}' ...")
    open(gdext_path, 'w').write(
        SCRIPTS_GDEXTENSION_IN.replace('@LIBRARY_NAME@', library_name))

    print(f"Configuring '{cpp_path}' ...")
    open(cpp_path, 'w').write(
        REGISTER_TYPES_CPP_IN.replace('@LIBRARY_NAME@', library_name))

    print(f"Configuring '{h_path}' ...")
    open(h_path, 'w').write(
        REGISTER_TYPES_H_IN.replace('@LIBRARY_NAME@', library_name))

    print("Files configured.")
    exit(0)

@PY_EMBED_SRC_FILES@

@CPPSCRIPT_PY_MODULE@

if __name__ == "__main__":
    # Ran as bindings generator

    import argparse, os, sys

    parser = argparse.ArgumentParser(
            prog='cppscript_bindings',
            description='Generates C++ bindings code for GDExtension')

    parser.add_argument('--header-name', type=str, nargs=1, required=True)
    parser.add_argument('--header-dir', type=str, nargs=1, required=True)
    parser.add_argument('--gen-dir', type=str, nargs=1, required=True)
    parser.add_argument('--auto-methods', type=bool, default=True)
    parser.add_argument('--definitions', type=str, nargs='*')
    parser.add_argument('--include-paths', type=str, nargs='*')
    parser.add_argument('sources', nargs='*')

    args = parser.parse_args(sys.argv[1:])
    env = {
        'header_name' : args.header_name[0],
        'header_dir' : args.header_dir[0],
        'gen_dir' : args.gen_dir[0],
        'compile_defs' : set(args.definitions),
        'include_paths' :  set(args.include_paths),
        'auto_methods' : args.auto_methods
    }

    sys.exit(generate_header_cmake(args.sources, env))

