import argparse, os, sys

# Hack to not import SCons
os.environ['NOT_SCONS'] = '1'
from cppscript import generate_header_cmake

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
	'compile_defs' : args.definitions,
	'include_paths' :  args.include_paths,
	'auto_methods' : args.auto_methods
}

sys.exit(generate_header_cmake(args.sources, env))

