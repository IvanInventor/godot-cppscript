import re
import clang.cindex
import json

REGENERATE = False
scripts = []
# TODO
#	Register class
#	Register abstract class
#	Generate _bind_methods:
#		Simple bind
#		With args decsription
#		With DEFVAL
#		Static methods
#		With varargs
#	Properties
#	Group/subgroup of properties
#	Signals
#
#	Constants
#	Enums
#	Bitfields
#
#	Constants w/o class
#	Enums w/o class
#	
#	RPCs
########## CLANG
def extract_methods_and_fields(translation_unit):

	godot_class = {}
	current_class = None
	current_access = 'private'
	macros = []
	def parse_class(parent, class_name):
		for cursor in parent.get_children():

			#print(vars(cursor.extent.start).items())
			match cursor.kind:
				case clang.cindex.CursorKind.CXX_ACCESS_SPEC_DECL:
					current_access = cursor.spelling

				case clang.cindex.CursorKind.CXX_BASE_SPECIFIER:
					godot_class[class_name]['base'] = cursor.type.spelling

				case clang.cindex.CursorKind.CXX_METHOD:
					godot_class[class_name]['methods'].append({	   'name' : cursor.spelling,
									   'return' : cursor.result_type.spelling,
									   'args' : [(arg.type.spelling, arg.spelling) for arg in cursor.get_arguments()],
									   'position' : cursor.extent.start.offset
						})
				case clang.cindex.CursorKind.FIELD_DECL:
					godot_class[class_name]['properties'].append({ 	'type' : cursor.type.spelling,
				       						'name' : cursor.spelling,
				       						'position' : cursor.extent.start.offset})


	def parse_cursor(cursor):
		#print(cursor.kind)
		#print([i.spelling for i in cursor.get_tokens()])
		match cursor.kind:
			case clang.cindex.CursorKind.CLASS_DECL:
				tokens = cursor.get_tokens()
				for token in tokens:
					if token.spelling == ':': # base class declaration after
						m = [next(tokens).spelling, next(tokens).spelling]
						match m:
							case ['public' | 'private' | 'protected', base] | [base]:
								current_class = cursor.spelling
								godot_class[current_class] = {	'properties' : [],
												'methods' : [],
												'base' : base
									}
								parse_class(cursor, current_class)
							case _:
								return

			case clang.cindex.CursorKind.MACRO_INSTANTIATION:
				match cursor.spelling:
					case 'GCLASS':
						pass

					case 'GPROPERTY':
						pass



		for child in cursor.get_children():
			parse_cursor(child)


	parse_cursor(translation_unit.cursor)
	# Recursively traverse the child nodes
	
	return godot_class

def parse_cpp_file(filename):
	index = clang.cindex.Index.create()
	translation_unit = index.parse(filename, args=['-DGDCLASS', '-I.'], options=clang.cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD)

	if not translation_unit:
		print("Error: Failed to parse the translation unit!")
		return

	#return extract_methods_and_fields(translation_unit)
	data = extract_methods_and_fields(translation_unit)
	return data

def generate_register_header(target, source, env):
	#TODO: fix always false
	#if env['REGENERATE'] == False:
	#	return

	print('-------------- GENERATING HEADER ---------------')
	defs = env['defs']
	header = ''
	# Generate include headers
	for file in scripts:
		header += f'#include <{file}>\n'
	# Generate register_classes function
	register_classes_str = 'inline void register_script_classes() {\n'
	register_classes_str += ''.join([f"ClassDB::register_class<{i}>();\n" for i in defs.keys()])
	register_classes_str += '}\n'
	header += register_classes_str
	# Generate _bind_methods for each class
	bind_methods_all_str = ''
	for class_name, content in defs.items():
		bind = f'void {class_name}::_bind_methods() {{\n'
		
		for method in content['methods']:
			#TODO: refer to "Generate _bind_methods"
			bind += f'	ClassDB::bind_method(D_METHOD("{method["name"]}"), &{class_name}::{method["name"]});\n'

		for prop in content['properties']:
			pass
			#TODO
			#bind += f'ADD_PROPERTY(PropertyInfo(Variant::VECTOR2, "group_subgroup_custom_position"), "set_custom_position", "get_custom_position");'

		bind += '};\n\n'
		header += bind

	with open('scripts.gen.h', 'w') as file:
		file.write(header)
	
	save_defs(defs)

########### CLANG
SPP_DEFS_FILE = '.spp_defs'
def load_defs():
	try:
		with open(SPP_DEFS_FILE, 'r') as file:
			return json.load(file)
	except:
		return {}

def save_defs(defs):
	print("Saving: *****", defs)
	with open(SPP_DEFS_FILE, 'w') as file:
		json.dump(defs, file)

def build_scripts(target, source, env):
	global REGENERATE
	if not REGENERATE:
		REGENERATE = True
		env['defs'] = load_defs()
	
	header = str(source[0])[:-4] + '.hpp'
	data = parse_cpp_file(header)
	env['defs'] |= data
	#print("Parsed definitions: ", defs[str(source[0])])
	


def emitter(target, source, env):
	sources = [str(i) for i in source if str(i) != 'register_types.os']
	for src in sources:
		env.AddPreAction(str(src), build_scripts)
	return target, source

envcpp = SConscript('godot-cpp/SConstruct')
env = envcpp.Clone()
env.Append(CPPPATH='.')
#env = Environment()
#env['suffix'] = '.o'
sources = Glob("src/*.cpp", exclude=['register_types.cpp'])
scripts = [str(i) for i in Glob("src/*.hpp")]
#env['REGENERATE'] = False
#env['register_classes'] = []
#TEST

env.Append(LIBEMITTER=emitter)

library_name = 'bin/libscripts' + env['OBJSUFFIX']
static_library = env.StaticLibrary(
	library_name,
	source=sources
	)

env.AddPostAction(static_library, generate_register_header)

env.Append(LIBPATH=['bin/'])
env.Append(LIBs=[static_library[0]])
library = env.SharedLibrary(
		'#bin/libscripts{}{}'.format(env['suffix'], env['LIBSUFFIX']),
		source=['register_types.cpp']
		)
env.Depends(library, static_library)
env.Ignore(library, 'scripts.gen.h')
Default(library)
