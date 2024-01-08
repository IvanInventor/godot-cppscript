import argparse, os, sys

# Hack to not import SCons
os.environ['NOT_SCONS'] = '1'
from cppscript import generate_header_cmake

parser = argparse.ArgumentParser(
		prog='cppscript_bindings',
		description='Generates C++ bindings code for GDExtension')

parser.add_argument('--src', type=str, nargs=1, required=True)
parser.add_argument('--gen-dir', type=str, nargs=1, required=True)
parser.add_argument('--defs-file', type=str, nargs=1, required=True)
parser.add_argument('--gen-header', type=str, nargs=1, required=True)
parser.add_argument('--auto-methods', type=bool, default=True)
parser.add_argument('sources', nargs='*')

args = parser.parse_args(sys.argv[1:])

env = {	'src' : args.src[0],
       	'gen_dir' : args.gen_dir[0],
	'defs_file' : args.defs_file[0],
	'gen_header' : args.gen_header[0],
	'auto_methods' : args.auto_methods
}

sys.exit(generate_header_cmake(args.gen_header, args.sources, env))

