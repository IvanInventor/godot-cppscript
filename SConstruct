import clang.cindex


SCRIPTS_PATH = 'src/'
KEYWORDS = ['GMETHOD', 'GPROPERTY', 'GGROUP', 'GSUBGROUP', 'GCONSTANT', 'GBITFIELD']
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
#	+- Properties
#	+ Group/subgroup of properties
#	Signals
#
#	+ Constants
#	+ Enums
#		Outside of class
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
	while i < len(list):
		if key(list[i]) == True:
			collapsed.append(action(list[i], list[tail:i]))
			i += 1
			tail = i
		else:
			i += 1

	return collapsed, list[tail:i]


def extract_methods_and_fields(translation_unit):

	classes = []
	found_classes = []
	macros = []
	bases_temp = {}
	def parse_class(parent, class_cursors):
		for cursor in parent.get_children():
			match cursor.kind:
				case clang.cindex.CursorKind.CXX_METHOD:
					if cursor.access_specifier == clang.cindex.AccessSpecifier.PUBLIC:
						class_cursors.append(cursor)
					
				case clang.cindex.CursorKind.FIELD_DECL:
					if cursor.access_specifier == clang.cindex.AccessSpecifier.PUBLIC:
						class_cursors.append(cursor)
								
				case clang.cindex.CursorKind.ENUM_DECL:
					if cursor.access_specifier == clang.cindex.AccessSpecifier.PUBLIC:
						class_cursors.append(cursor)

	def parse_cursor(cursor):
		match cursor.kind:
			case clang.cindex.CursorKind.CLASS_DECL:
				found_classes.append(cursor)

			case clang.cindex.CursorKind.MACRO_INSTANTIATION:
				if cursor.spelling in KEYWORDS:
					macros.append(cursor)
				
				if cursor.spelling.startswith('GEXPORT_'):
					macros.append(cursor)
					
				match cursor.spelling:
					case 'GCLASS':
						found_classes.append(cursor)
						tokens = list(cursor.get_tokens())

					case 'GPROPERTY':
						pass
					



		for child in cursor.get_children():
			parse_cursor(child)
	

	parse_cursor(translation_unit.cursor)

	found_class = sorted(found_classes, key=lambda x: x.extent.start.offset, reverse=True)	

	def add_class(cursor, macros):
		if len(macros) > 1:
			raise Exception(f'Incorrect usage of GCLASS at <{macros[1].location.file.name}>:{macros[1].location.line}:{macros[1].location.column}')
		
		for macro in macros:
			classes.append((cursor, list(macro.get_tokens())[4].spelling)) # Temporary base name resolution

	collapse_list(found_class, lambda x: x.kind == clang.cindex.CursorKind.CLASS_DECL, add_class)
		
	parsed_classes = {}
	for cursor, base in classes:
		class_defs = {
			'base' : base,
			'methods' : [],
			'properties' : [],
			'groups' : set(),
			'subgroups' : set(),
			'enum_constants' : {},
			'enum_unnamed' : set(),
			'constants' : set(),
			'bitfields' : {}}
		child_cursors = []
		parse_class(cursor, child_cursors)
		group, subgroup = '', ''
		start, end = cursor.extent.start.offset, cursor.extent.end.offset
		class_macros = sorted([m for m in macros if start < m.extent.start.offset < end] + child_cursors, key=lambda x: x.extent.start.offset)

		def apply_macros(item, macros):
			nonlocal group
			nonlocal subgroup
			properties = None
			match item.kind:
				case clang.cindex.CursorKind.CXX_METHOD:
					#TODO: add all reserved methods
					if item.spelling not in ['_process', '_physics_process']:
						properties = {
							'name' : item.spelling,
							'return' : item.result_type.spelling,
							'args' : [(arg.type.spelling, arg.spelling) for arg in item.get_arguments()],
							'is_static' : item.is_static_method()}

				case clang.cindex.CursorKind.ENUM_DECL:
					properties = []
					if item.type.spelling[-1] != ')':
						enum_type = 'enum_constants'

					for enum in item.get_children():
						if enum.kind == clang.cindex.CursorKind.ENUM_CONSTANT_DECL:
							properties.append(enum.spelling)

				case clang.cindex.CursorKind.FIELD_DECL:
					properties = {
						'name' : '',
						'type' : '',
						'setter' : '',
						'getter' : '',
						'hint' : 'PROPERTY_HINT_NONE',
						'hint_string' : '',
						'is_static' : item.is_static_method()
						}
			
			for macro in macros:
				if macro.spelling.startswith('GEXPORT_'):
					properties |= {
						'hint' : 'PROPERTY_HINT_' + macro.spelling[8:],
						'hint_string' : ''.join([i.spelling for i in macro.get_tokens()][2:-1])
						}
					continue

				match macro.spelling:
					case 'GMETHOD':
						pass

					case 'GPROPERTY':
						# fail check here
						if item.kind != clang.cindex.CursorKind.FIELD_DECL:
							#TODO line:column error
							raise Exception(f'Incorrect macro usage at {macro.location.line}:{macro.location.column}')

						args = ''.join([i.spelling for i in macro.get_tokens()][2:-1]).split(',')
						if len(args) != 2:
							raise Exception(f'Incorrect macro usage at <{macro.location.file.name}>:{macro.location.line}:{macro.location.column}')

					
						# Workaround
						tokens = [i.spelling for i in item.get_tokens()]
						type = ''.join(tokens[:tokens.index(item.spelling)])
						properties |= {
								'type' : type,
								'setter' : args[0],
								'getter' : args[1]
								}

					case 'GGROUP':
						group = ' '.join([i.spelling for i in macro.get_tokens()][2:-1])
						if group != '':
							class_defs['groups'].add((group, group.lower().replace(" ", "") + "_"))
						subgroup = ''

					case 'GSUBGROUP':
						subgroup = ' '.join([i.spelling for i in macro.get_tokens()][2:-1])
						if subgroup != '':
							class_defs['subgroups'].add((subgroup, group.lower().replace(" ", "") + "_" + subgroup.lower().replace(" ", "") + "_"))


					case 'GBITFIELD':
						if item.kind != clang.cindex.CursorKind.ENUM_DECL:
							raise Exception(f'Incorrect macro usage at <{macro.location.file.name}>:{macro.location.line}:{macro.location.column}')

						if item.type.spelling[-1] == ')':
							raise Exception(f'Bitfield must be named enum <{macro.location.file.name}>:{macro.location.line}:{macro.location.column}')

						enum_type = 'bitfields'

			match item.kind:
				case clang.cindex.CursorKind.CXX_METHOD:
					if properties != None:
						class_defs['methods'].append(properties)

				case clang.cindex.CursorKind.ENUM_DECL:
					if item.type.spelling[-1] != ')':
						class_defs[enum_type][item.type.spelling] = properties
					else:
						class_defs['constants'] = properties

				case clang.cindex.CursorKind.FIELD_DECL:
					name = ("" if group == "" else group.lower().replace(" ", "") + "_") + ("" if subgroup == "" else subgroup.lower().replace(" ", "") + "_") + item.spelling
					properties |= {'name': name}

					class_defs['properties'].append(properties)

			return item

						
		collapse_list(class_macros, lambda x: x.kind != clang.cindex.CursorKind.MACRO_INSTANTIATION, apply_macros)
		#print(json.dumps(class_defs, sort_keys=True, indent=2, default=lambda x: x if not isinstance(x, set) else list(x)))
		parsed_classes[cursor.spelling] = class_defs

	return parsed_classes

def parse_cpp_file(filename):
	index = clang.cindex.Index.create()
	translation_unit = index.parse(filename, args=['-DGDCLASS', '-Isrc'], options=clang.cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD)

	if not translation_unit:
		print("Error: Failed to parse the translation unit!")
		return

	data = extract_methods_and_fields(translation_unit)
	return data

def generate_register_header():
	defs = {}
	for s in scripts:
		defs |= parse_cpp_file(s)

	
	#print(json.dumps(defs, sort_keys=True, indent=2, default=lambda x: x if not isinstance(x, set) else list(x)))
	"""	class_defs = {
			'base' : bases_temp[cursor.spelling],
			'methods' : [],
			'properties' : [],
			'groups' : set(),
			'subgroups' : set(),
			'enum_constants' : set(),
			'constants' : set()
			}
			"""
	header = ''
	# Generate include headers
	for file in scripts:
		#TEMPORARY FIX of <src/****>
		header += f'#include "{file[4:]}"\n'
	
	header += '\nusing namespace godot;\n\n'
	# Generate register_classes function
	register_classes_str = 'inline void register_script_classes() {\n'
	register_classes_str += ''.join([f"	ClassDB::register_class<{i}>();\n" for i in defs.keys()])
	register_classes_str += '}\n'
	header += register_classes_str
	# Generate _bind_methods for each class
	for class_name, content in defs.items():
		bind = f'void {class_name}::_bind_methods() {{\n'
		outside_bind = ''
		
		#Groups/subgroups declarations
		for group, name in content['groups']:
			bind += f'	ADD_GROUP("{group}", "{name}");\n'

		for group, name in content['subgroups']:
			bind += f'	ADD_SUBGROUP("{group}", "{name}");\n'

		for method in content['methods']:
			#TODO: refer to "Generate _bind_methods"
			args = ''.join([f', "{argname}"' if argname != '' else '' for argtype, argname in method['args']])
			if method['is_static']:
				bind += f'	ClassDB::bind_static_method("{class_name}", D_METHOD("{method["name"]}"{args}), &{class_name}::{method["name"]});\n'
			else:
				bind += f'	ClassDB::bind_method(D_METHOD("{method["name"]}"{args}), &{class_name}::{method["name"]});\n'

		for prop in content['properties']:
			bind += f'	ADD_PROPERTY(PropertyInfo(GetTypeInfo<{prop["type"]}>::VARIANT_TYPE, "{prop["name"]}", {prop["hint"]}, "{prop["hint_string"]}"), "{prop["setter"]}", "{prop["getter"]}");\n'

		for enum, consts in content['enum_constants'].items():
			#TODO: generate inside class header
			outside_bind += f'VARIANT_ENUM_CAST({enum});\n'
			for const in consts:
				bind += f'	BIND_ENUM_CONSTANT({const});\n'

		for enum, consts in content['bitfields'].items():
			#TODO: generate inside class header
			outside_bind += f'VARIANT_BITFIELD_CAST({enum});\n'
			for const in consts:
				bind += f'	BIND_BITFIELD_FLAG({const});\n'

		for const in content['enum_unnamed']:
			bind += f'	BIND_CONSTANT({const});\n'

		for const in content['constants']:
			bind += f'	BIND_CONSTANT({const});\n'

		bind += '};\n'
		bind += outside_bind + '\n'

		header += bind

	#print(json.dumps(defs, sort_keys=True, indent=2, default=lambda x: x if not isinstance(x, set) else list(x)))
	with open(SCRIPTS_PATH + 'scripts.gen.h', 'w') as file:
		file.write(header)
	

env = SConscript('godot-cpp/SConstruct')
env.Append(CPPPATH=[SCRIPTS_PATH])

#register_types.cpp must be last one
sources = Glob("src/*.cpp", exclude=['src/register_types.cpp']) + Glob('src/register_types.cpp')

#parsing only .hpp headers
scripts = [str(i) for i in Glob("src/*.hpp")]

generate_register_header()

library_name = 'libscripts' + env['suffix'] + env['LIBSUFFIX']

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

env.Ignore(library, SCRIPTS_PATH + 'scripts.gen.h')
Default(library)
