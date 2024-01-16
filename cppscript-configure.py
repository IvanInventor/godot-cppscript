#!/usr/bin/env python3

import os, sys

try:
	library_name_full = sys.argv[1]
	src_dir = sys.argv[2]
	project_dir = sys.argv[3]
except:
	print('ERROR: Not enough arguments.\nUsage:\n\tcmake -P cppscript/cppscript-configure.cmake <library_name> <src_dir> <project_dir>', file=sys.stderr)
	exit(1)

library_name = library_name_full.replace('-', '_')

def replace(in_path, out_path):
	with open(in_path, 'r') as infile:
		text = infile.read()
	with open(out_path, 'w') as outfile:
		outfile.write(text.replace('@LIBRARY_NAME@', library_name))

print(f"Configuring '{os.path.join(project_dir, f'{library_name_full}.gdextension')}' ...")
replace(os.path.join(os.path.dirname(__file__), 'templates', 'scripts.gdextension.in'), os.path.join(project_dir, f'{library_name_full}.gdextension'))

print(f"Configuring '{os.path.join(src_dir, 'register_types.cpp')}' ...")
replace(os.path.join(os.path.dirname(__file__), 'templates', 'register_types.cpp.in'), os.path.join(src_dir, 'register_types.cpp'))

print(f"Configuring '{os.path.join(src_dir, 'register_types.h')}' ...")
replace(os.path.join(os.path.dirname(__file__), 'templates', 'register_types.h.in'), os.path.join(src_dir, 'register_types.h'))

print("Files configured.")
