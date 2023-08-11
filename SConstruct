import re
import clang.cindex
import json

REGENERATE = False
SCRIPTS_GEN_PATH = 'src/scripts.gen.h'
KEYWORDS = ['GMETHOD', 'GPROPERTY', 'GGROUP', 'GSUBGROUP']
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
#	+ Group/subgroup of properties
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

def collapse_list(list, key, action):
	collapsed = []
	i = 0
	tail = 0
	for i in range(len(list)):
		if key(list[i]) == True:
			collapsed.append(action(list[i], list[tail:i]))
			i += 1
			tail = i
		else:
			i += 1

	return collapsed, list[tail:i]

########## CLANG
def apply_macros(target, macros):
	pass

def extract_methods_and_fields(translation_unit):

	classes = {}
	macros = []
	def parse_class(parent, class_name):
		classes[class_name]['position'] = parent.extent.start.offset
		classes[class_name]['end'] = parent.extent.end.offset
		for cursor in parent.get_children():
			match cursor.kind:
				#case clang.cindex.CursorKind.CXX_ACCESS_SPEC_DECL:
				#	current_access = cursor.access_specifier
				#	print('----------- ACCESS --------------')
				#	print(current_access)

				case clang.cindex.CursorKind.CXX_BASE_SPECIFIER:
					classes[class_name]['base'] = cursor.type.spelling

				case clang.cindex.CursorKind.CXX_METHOD:
					if cursor.access_specifier == clang.cindex.AccessSpecifier.PUBLIC:
						classes[class_name]['methods'].append({	   'name' : cursor.spelling,
					     						'token_type' : 'method',
										   'return' : cursor.result_type.spelling,
										   'args' : [(arg.type.spelling, arg.spelling) for arg in cursor.get_arguments()],
										   'position' : cursor.extent.start.offset,
										   'is_static' : cursor.is_static_method()
							})
				case clang.cindex.CursorKind.FIELD_DECL:
					classes[class_name]['properties'].append({ 	'type' : cursor.type.spelling,
					       						'token_type' : 'property',
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
				if cursor.spelling in KEYWORDS:
					macros.append({	'macros_name': cursor.spelling,
		    					'position' : cursor.extent.start.offset,
		    					'content' : [t.spelling for t in cursor.get_tokens()][2:-1]})

				match cursor.spelling:
					case 'GCLASS':
						#OLD
						tokens = list(cursor.get_tokens())
						class_name, base = tokens[2].spelling, tokens[4].spelling
						classes[class_name] = {		'properties' : [],
										'methods' : [],
										'base' : base,
			     							'groups' : set(),
			     							'subgroups' : set()
									}
						pass

					case 'GPROPERTY':
						pass
					



		for child in cursor.get_children():
			parse_cursor(child)
	

	parse_cursor(translation_unit.cursor)
	# Recursively traverse the child nodes
	# Map macros to methods/properties
	for class_name, content in classes.items():
		start, end = content['position'], content['end']
		class_macros = [m for m in macros if start < m['position'] < end]
		class_macros += content['methods'] + content['properties']
		class_macros = sorted(class_macros, key=lambda x: x['position'])
		group = ['', '']
		#print('************ APPLY MACROS ***********')
		#print(json.dumps(class_macros, sort_keys=True, indent=2))
		#print(json.dumps(class_macros, sort_keys=True, indent=2))

		def apply_macros(item, macros):
			print('========= Applying ============')
			print(json.dumps(item, sort_keys=True, indent=2))
			print(json.dumps(macros, sort_keys=True, indent=2))

			for macro in macros:
				match macro['macros_name']:
					case 'GMETHOD':
						item |= {'TEST' : True}
						print('***** ADDED TEST ****')
						# fail check here
						pass
					case 'GPROPERTY':
						# fail check here
						type, setter, getter = ''.join(macro['content']).split(',')
						item['name'] = group[0] + group[1] + item['name']
						item |= {'register' : { 'type' : type,
			     						'setter' : setter,
			     						'getter' : getter
			     						}}
					case 'GGROUP':
						group[0] = ' '.join(macro['content'])
						if group[0] != '':
							classes[class_name]['groups'].add(group[0])
							group[0] = group[0].lower().replace(' ', '_') + '_' 
						group[1] = ''

					case 'GSUBGROUP':
						group[1] = ' '.join(macro['content'])
						if group[1] != '':
							classes[class_name]['subgroups'].add(group[1])
							group[1] = group[1].lower().replace(' ', '_') + '_'

			return item

						
		collapse_list(class_macros, lambda x: 'name' in x.keys(), apply_macros)

	#print('---------- END OF PARSING ------------')
	#for class_name, content in classes.items():
	#	start, end = content['position'], content['end']
	#	class_macros = [m for m in macros if start < m['position'] < end]
	#	class_macros += content['methods'] + content['properties']
	#	class_macros = sorted(class_macros, key=lambda x: x['position'])
	#	print(class_name)
	#	print(json.dumps(class_macros, sort_keys=True, indent=2))

	#for c in classes.keys():
	#	macros.append(classes[c])
	#	macros.extend(classes[c]['properties'])
	#	macros.extend(classes[c]['methods'])
	#macros = sorted(macros, key=lambda x: x['position'])
	#print(json.dumps(macros, sort_keys=True, indent=2))
	return classes

def parse_cpp_file(filename):
	index = clang.cindex.Index.create()
	translation_unit = index.parse(filename, args=['-DGDCLASS', '-Isrc'], options=clang.cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD)

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
		#TEMP FIX of <src/****>
		header += f'#include "{file[4:]}"\n'
	
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
		
		#Groups/subgroups declarations
		for g in content['groups']:
			bind += f'	ADD_GROUP("{g}", "{g.lower().replace(" ", "_") + "_"}");\n'

		for g in content['subgroups']:
			bind += f'	ADD_SUBGROUP("{g}", "{g.lower().replace(" ", "_") + "_"}");\n'

		for method in content['methods']:
			#TODO: refer to "Generate _bind_methods"
			args = ''.join([f', "{m[1]}"' for m in method['args']])
			bind += f'	ClassDB::bind_method(D_METHOD("{method["name"]}"{args}), &{class_name}::{method["name"]});\n' \
					if method['is_static'] == False else \
				f'	ClassDB::bind_static_method("{class_name}", D_METHOD("{method["name"]}"{args}), &{class_name}::{method["name"]});\n'

		for prop in [p for p in content['properties'] if 'register' in p.keys()]:
			bind += f'	ADD_PROPERTY(PropertyInfo({prop["register"]["type"]}, "{prop["name"]}"), "{prop["register"]["setter"]}", "{prop["register"]["getter"]}");\n'

		bind += '};\n\n'
		header += bind
	print('--- DEFS ---')

	print(json.dumps(defs, sort_keys=True, indent=2, default=lambda x: x if not isinstance(x, set) else list(x)))
	with open(SCRIPTS_GEN_PATH, 'w') as file:
		file.write(header)
	
	#save_defs(defs)

########### CLANG
SPP_DEFS_FILE = '.spp_defs'
def load_defs():
	try:
		with open(SPP_DEFS_FILE, 'r') as file:
			return json.load(file)
	except:
		return {}

def save_defs(defs):
	print("Saving: *****")
	print(defs)
	#print(json.dumps(defs, sort_keys=True, indent=2))
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

library_name = 'libscripts-static' + env['suffix'] + env['LIBSUFFIX']
print(env['suffix'] + '_' + env['LIBSUFFIX'])
static_library = env.StaticLibrary(
	'bin/' + library_name,
	source=sources
	)

print(static_library)
env.AddPreAction(static_library[0], generate_register_header)

#env.Append(LIBPATH=['godot-coo/bin'])
#env.Append(LIBS="libgodot-cpp{}{}".format(env['suffix'], env["LIBSUFFIX"]))

#env.Append(LIBPATH=['bin'])
#env.Append(LIBS=[library_name])

#print(env['LIBPATH'])
#print(env['LIBS'])
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
        source=['src/register_types.cpp' + 'src/' + library_name],
    )

env.Requires(library, static_library)
env.Ignore(library, SCRIPTS_GEN_PATH)
Default(library)
