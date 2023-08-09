import re
import clang.cindex
import json

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

	def parse_class(parent, class_name):
		for cursor in parent.get_children():

			print(cursor.kind)
			print(int(cursor.extent.start.offset))
			#print(vars(cursor.extent.start).items())
			print([i.spelling for i in cursor.get_tokens()])
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
					godot_class['properties'].append({ 	'type' : cursor.type.spelling,
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
						print('----- PARSING GDCLASS ---------')

					case 'GPROPERTY':
						print('----- PARSING GPROPERTY ---------')
						macros_locations.append(cursor.extent.start.offset)



		for child in cursor.get_children():
			parse_cursor(child)


	parse_cursor(translation_unit.cursor)
	# Recursively traverse the child nodes
	
	print('------------ MACROS LOCATIONS -------------')
	print(macros_locations)
	print('------------ PROPERTIES LOCATIONS -------------')
	print(props_locations)
	return godot_class

def parse_cpp_file(filename):
	index = clang.cindex.Index.create()
	translation_unit = index.parse(filename, args=['-DGDCLASS'], options=clang.cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD)

	if not translation_unit:
		print("Error: Failed to parse the translation unit!")
		return

	#return extract_methods_and_fields(translation_unit)
	data = extract_methods_and_fields(translation_unit)
	print(f'Parsed data from {filename}:')
	print(json.dumps(data, indent=2, sort_keys=True))

def generate_register_header(target, source, env):
	if env['REGENERATE'] == False:
		return

	defs = env['defs']
	print('-------------- GENERATING HEADER ---------------')
	header = ''
	for file, class_defs in defs.items():
		print(file, class_defs)
		# class ClassName : Base {
		header += f"class {class_defs['name']} : {class_defs['base']} {{\n"
		
		# GDCLASS(ClassName, Base);
		#header += f"GDCLASS({class_defs['name']}, {class_defs['base']});\n"

		# _bind_methods
		header += f"static void _bind_methods();\n"
		# Properties
		header += '\n'.join([f"{p['type']} {p['name']};" for p in class_defs['properties']]) + '\n'
		# Methods
		header += '\n'.join([f"{p['return']} {p['name']}({', '.join([arg['name'] for arg in p['args']])});" for p in class_defs['methods']]) + '\n'

		header += '};\n'

		header += f"void {class_defs['name']}::_bind_methods() {{\n"
		header += '}\n'
	
	header += 'void register_script_classes() {\n'
	# place registers here
	header += '}\n'

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
	with open(SPP_DEFS_FILE, 'w') as file:
		json.dump(defs, file)

def build_scripts(target, source, env):
	if env['REGENERATE'] == False:
		env['REGENERAGE'] = True
		env['defs'] = load_defs()
	
	env['defs'][str(source[0])] = parse_cpp_file(str(source[0]))
	#print("Parsed definitions: ", defs[str(source[0])])
	


def emitter(target, source, env):
	sources = [str(i) for i in source if str(i) != 'register_types.os']
	for src in sources:
		env.AddPreAction(str(src), build_scripts)
	return target, source

envcpp = SConscript('godot-cpp/SConstruct')
env = envcpp.Clone()
#env = Environment()
#env['suffix'] = '.o'
sources = Glob("*.cpp", exclude=['register_types.cpp'])
env['REGENERATE'] = False
#TEST

env.Append(LIBEMITTER=emitter)

static_library = env.StaticLibrary(
	'#bin/libscripts' + env['OBJSUFFIX'],
	source=sources
	)

env.AddPostAction(static_library[0], generate_register_header)
print(static_library)

env.Append(LIBPATH=['bin/'])
env.Append(LIBs=[static_library[0]])
library = env.SharedLibrary(
		'#bin/libscripts{}{}'.format(env['suffix'], env['LIBSUFFIX']),
		source=['register_types.cpp']
		)
env.Depends(library, static_library)
env.Ignore(library, 'scripts.gen.h')
Default(library)
