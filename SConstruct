import re
import clang.cindex
import json


CPPPATH = 'src/'
KEYWORDS = ['GMETHOD', 'GPROPERTY', 'GGROUP', 'GSUBGROUP', 'GCONSTANT']
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

	classes = []
	macros = []
	bases_temp = {}
	def parse_class(parent, class_cursors):
		for cursor in parent.get_children():
			match cursor.kind:
				case clang.cindex.CursorKind.CXX_BASE_SPECIFIER:
					#temp
					#classes[class_name]['base'] = cursor.type.spelling
					pass

				case clang.cindex.CursorKind.CXX_METHOD:
					if cursor.access_specifier == clang.cindex.AccessSpecifier.PUBLIC:
						class_cursors.append(cursor)
					
				case clang.cindex.CursorKind.FIELD_DECL:
					class_cursors.append(cursor)
								
				case clang.cindex.CursorKind.ENUM_DECL:
					class_cursors.append(cursor)
					for enum in cursor.get_children():
						if enum.kind == clang.cindex.CursorKind.ENUM_CONSTANT_DECL:
							class_cursors.append(enum)
						
	def parse_cursor(cursor):
		match cursor.kind:
			case clang.cindex.CursorKind.CLASS_DECL:
				# rewrite after GCLASS implement
				cursors = []
				classes.append((cursor, cursors))
				parse_class(cursor, cursors)

			case clang.cindex.CursorKind.MACRO_INSTANTIATION:
				if cursor.spelling in KEYWORDS:
					macros.append(cursor)
					
				match cursor.spelling:
					case 'GCLASS':
						#TODO
						tokens = list(cursor.get_tokens())
						bases_temp[tokens[2].spelling] = tokens[4].spelling

					case 'GPROPERTY':
						pass
					



		for child in cursor.get_children():
			parse_cursor(child)
	

	parse_cursor(translation_unit.cursor)
	# Recursively traverse the child nodes
	# Map macros to methods/properties
	parsed_classes = {}
	for cursor, child_cursors in classes:
		class_defs = {
			'base' : bases_temp[cursor.spelling],
			'methods' : [],
			'properties' : [],
			'groups' : set(),
			'subgroups' : set(),
			'enum_constants' : {},
			'enum_unnamed' : set(),
			'constants' : set()
			}
		group = ['', '']
		start, end = cursor.extent.start.offset, cursor.extent.end.offset
		class_macros = sorted([m for m in macros if start < m.extent.start.offset < end] + child_cursors, key=lambda x: x.extent.start.offset)
		#print('************ APPLY MACROS ***********')
		#print(json.dumps(class_macros, sort_keys=True, indent=2, default=lambda x: (x.extent.start.offset, x.spelling)))

		def apply_macros(item, macros):
			#print('========= Applying ============')
			#print(item)
			#print(macros)

			if item.kind == clang.cindex.CursorKind.CXX_METHOD:
				class_defs['methods'].append({
							'name' : item.spelling,
							'return' : item.result_type.spelling,
							'args' : [(arg.type.spelling, arg.spelling) for arg in item.get_arguments()],
							'is_static' : item.is_static_method()})

				print([[j.spelling for j in i.get_tokens()] for i in item.get_children()])
				print([i.spelling for i in item.get_tokens()])
				print([[j.spelling for j in i.get_tokens()] for i in item.get_arguments()])

			for macro in macros:
				match macro.spelling:
					case 'GMETHOD':
						pass

					case 'GPROPERTY':
						# fail check here
						if item.kind != clang.cindex.CursorKind.FIELD_DECL:
							#TODO line:column error
							raise Exception('Incorrect macro usage')

						args = ''.join([i.spelling for i in macro.get_tokens()][2:-1]).split(',')
						if len(args) != 3:
							raise Exception('Incorrect macro usage')

						name = group[0] + group[1] + item.spelling
						class_defs['properties'].append([name] + args)

					case 'GGROUP':
						group[0] = ' '.join([i.spelling for i in macro.get_tokens()][2:-1])
						if group[0] != '':
							class_defs['groups'].add(group[0])
							group[0] = group[0].lower().replace(' ', '_') + '_'
						group[1] = ''

					case 'GSUBGROUP':
						group[1] = ' '.join([i.spelling for i in macro.get_tokens()][2:-1])
						if group[1] != '':
							class_defs['subgroups'].add(group[1])
							group[1] = group[1].lower().replace(' ', '_') + '_'

					case 'GCONSTANT':
						print('GCONSTANT')
						print(item.type.spelling)
						has_name = item.type.spelling[-1] != ')'
						if item.kind == clang.cindex.CursorKind.ENUM_DECL:
							for enum in item.get_children():
								if enum.kind == clang.cindex.CursorKind.ENUM_CONSTANT_DECL:
									if has_name :
										enums = class_defs['enum_constants'].get(enum.type.spelling, set())
										enums.add(enum.spelling)
										class_defs['enum_constants'][enum.type.spelling] = enums
									else:
										class_defs['enum_unnamed'].add(enum.spelling)

						elif item.kind == clang.cindex.CursorKind.ENUM_CONSTANT_DECL:
							if has_name:
								enums = class_defs['enum_constants'].get(item.type.spelling, set())
								enums.add(item.spelling)
								class_defs['enum_constants'][item.type.spelling] = enums
								
							else:
								class_defs['enum_unnamed'].add(item.spelling)
						
						else:
							raise Exception('Incorrect macro usage')
			return item

						
		collapse_list(class_macros, lambda x: x.kind != clang.cindex.CursorKind.MACRO_INSTANTIATION, apply_macros)
		print(json.dumps(class_defs, sort_keys=True, indent=2, default=lambda x: x if not isinstance(x, set) else list(x)))
		parsed_classes[cursor.spelling] = class_defs

	return parsed_classes

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

	
	print(json.dumps(defs, sort_keys=True, indent=2, default=lambda x: x if not isinstance(x, set) else list(x)))
	#print('-------------- GENERATING HEADER ---------------')
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
		#TEMP FIX of <src/****>
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
		for g in content['groups']:
			bind += f'	ADD_GROUP("{g}", "{g.lower().replace(" ", "_") + "_"}");\n'

		for g in content['subgroups']:
			bind += f'	ADD_SUBGROUP("{g}", "{g.lower().replace(" ", "_") + "_"}");\n'

		for method in content['methods']:
			#TODO: refer to "Generate _bind_methods"
			args = ''.join([f', "{m[1]}"' if m[1] != '' else '' for m in method['args']])
			if method['is_static']:
				bind += f'	ClassDB::bind_static_method("{class_name}", D_METHOD("{method["name"]}"{args}), &{class_name}::{method["name"]});\n'
			else:
				bind += f'	ClassDB::bind_method(D_METHOD("{method["name"]}"{args}), &{class_name}::{method["name"]});\n'

		for prop in content['properties']:
			name, type, getter, setter = prop
			bind += f'	ADD_PROPERTY(PropertyInfo({type}, "{name}"), "{setter}", "{getter}");\n'

		for enum, consts in content['enum_constants'].items():
			outside_bind += f'VARIANT_ENUM_CAST({enum});'
			for const in consts:
				bind += f'	BIND_ENUM_CONSTANT({const});\n'

		for const in content['enum_unnamed']:
			bind += f'	BIND_CONSTANT({const});\n'

		for const in content['constants']:
			bind += f'	BIND_CONSTANT({const});\n'

		bind += '};\n'
		bind += outside_bind + '\n'

		header += bind

	#print(json.dumps(defs, sort_keys=True, indent=2, default=lambda x: x if not isinstance(x, set) else list(x)))
	with open(CPPPATH + 'scripts.gen.h', 'w') as file:
		file.write(header)
	
	#save_defs(defs)

########### CLANG

env = SConscript('godot-cpp/SConstruct')

env.Append(CPPPATH=[CPPPATH])
sources = Glob("src/*.cpp", exclude=['src/register_types.cpp']) + Glob('src/register_types.cpp')
scripts = [str(i) for i in Glob("src/*.hpp")]
generate_register_header(None, None, None)

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

env.Ignore(library, CPPPATH + 'scripts.gen.h')
Default(library)
