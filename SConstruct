import re
import clang.cindex
import json

REGENERATE = False
SCRIPTS_GEN_PATH = 'src/scripts.gen.h'
scripts = []
# TODO
#	+ Register class
#	Register abstract class
#	Generate _bind_methods:
#		+ Simple bind
#		+ With args decsription
#		With DEFVAL
#		+ Static methods
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

	classes = {}
	current_access = 'private'
	macros = []
	def parse_class(parent, class_name):
		for cursor in parent.get_children():

			#print(vars(cursor.extent.start).items())
			match cursor.kind:
				case clang.cindex.CursorKind.CXX_ACCESS_SPEC_DECL:
					current_access = cursor.spelling

				case clang.cindex.CursorKind.CXX_BASE_SPECIFIER:
					classes[class_name]['base'] = cursor.type.spelling

				case clang.cindex.CursorKind.CXX_METHOD:
					classes[class_name]['methods'].append({	   'name' : cursor.spelling,
									   'return' : cursor.result_type.spelling,
									   'args' : [(arg.type.spelling, arg.spelling) for arg in cursor.get_arguments()],
									   'position' : cursor.extent.start.offset,
					    				   'is_static' : cursor.is_static_method()
						})
				case clang.cindex.CursorKind.FIELD_DECL:
					classes[class_name]['properties'].append({ 	'type' : cursor.type.spelling,
				       						'name' : cursor.spelling,
				       						'position' : cursor.extent.start.offset})


	def parse_cursor(cursor):
		#print(cursor.kind)
		#print([i.spelling for i in cursor.get_tokens()])
		match cursor.kind:
			case clang.cindex.CursorKind.CLASS_DECL:
				if cursor.spelling in classes.keys():
					parse_class(cursor, cursor.spelling)

			case clang.cindex.CursorKind.MACRO_INSTANTIATION:
				match cursor.spelling:
					case 'GCLASS':
						tokens = list(cursor.get_tokens())
						class_name, base = tokens[2].spelling, tokens[4].spelling
						classes[class_name] = {		'properties' : [],
										'methods' : [],
										'base' : base
									}
						pass

					case 'GPROPERTY':
						pass



		for child in cursor.get_children():
			parse_cursor(child)


	parse_cursor(translation_unit.cursor)
	# Recursively traverse the child nodes
	
	return classes

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
	defs = {}
	for s in scripts:
		defs |= parse_cpp_file(s)

	print('-------------- GENERATING HEADER ---------------')

	header = ''
	# Generate include headers
	for file in scripts:
		header += f'#include <{file}>\n'
	
	header += '\nusing namespace godot;\n\n'
	# Generate register_classes function
	register_classes_str = 'inline void register_script_classes() {\n'
	register_classes_str += ''.join([f"	ClassDB::register_class<{i}>();\n" for i in defs.keys()])
	register_classes_str += '}\n'
	header += register_classes_str
	# Generate _bind_methods for each class
	bind_methods_all_str = ''
	for class_name, content in defs.items():
		bind = f'void {class_name}::_bind_methods() {{\n'
		
		for method in content['methods']:
			#TODO: refer to "Generate _bind_methods"
			args = ''.join([f', "{m[1]}"' for m in method['args']])
			bind += f'	ClassDB::bind_method(D_METHOD("{method["name"]}"{args}), &{class_name}::{method["name"]});\n' \
					if method['is_static'] == False else \
				f'	ClassDB::bind_static_method("{class_name}", D_METHOD("{method["name"]}"{args}), &{class_name}::{method["name"]});\n'

		for prop in content['properties']:
			pass
			#TODO
			#bind += f'ADD_PROPERTY(PropertyInfo(Variant::VECTOR2, "group_subgroup_custom_position"), "set_custom_position", "get_custom_position");'

		bind += '};\n\n'
		header += bind

	with open(SCRIPTS_GEN_PATH, 'w') as file:
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

env = SConscript('godot-cpp/SConstruct')

env.Append(CPPPATH=["src/"])
sources = Glob("src/*.cpp", exclude=['src/register_types.cpp'])
scripts = [str(i) for i in Glob("src/*.hpp")]

#env.Append(LIBEMITTER=emitter)

library_name = 'bin/libscripts' + env['OBJSUFFIX']
static_library = env.StaticLibrary(
	library_name,
	source=sources
	)

env.AddPostAction(static_library, generate_register_header)

env.Append(LIBPATH=['bin/'])
env.Append(LIBS=[static_library[0]])

# For the reference:
# - CCFLAGS are compilation flags shared between C and C++
# - CFLAGS are for C-specific compilation flags
# - CXXFLAGS are for C++-specific compilation flags
# - CPPFLAGS are for pre-processor flags
# - CPPDEFINES are for pre-processor defines
# - LINKFLAGS are for linking flags

# tweak this if you want to use different folders, or more folders, to store your source code in.

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

env.Requires(library, static_library)
env.Ignore(library, SCRIPTS_GEN_PATH)
Default(library)
