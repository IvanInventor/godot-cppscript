from SCons.Script import *
import clang.cindex
import os, re


# TODO
#	+ Register class
#	+ Register abstract/virtual class
#	Generate _bind_methods:
#		+ Simple bind
#		+ With args decsription
#		+ With DEFVAL
#		+ Static methods
#		With varargs
#	+ Properties
#	+ Group/subgroup of properties
#	+ Signals
#
#	+ Constants
#	+ Enums
#	+ Bitfields
#
#	Constants w/o class
#	Enums w/o class
#	
#	RPCs


KEYWORDS = ['GMETHOD', 'GPROPERTY', 'GGROUP', 'GSUBGROUP', 'GCONSTANT', 'GBITFIELD', 'GSIGNAL']
scripts = []

# Helpers
def generate_header(target, source, env):
	#TODO: cache generated definitions
	generate_register_header(env, [str(i) for i in source], str(target[0]))


def generate_header_emitter(target, source, env):
	return env.File(os.path.join(env['src'], 'scripts.gen.h')), source

def collapse_list(list, key, action):
	i, tail = 0, 0
	while i < len(list):
		if key(list[i]) == True:
			action(list[i], list[tail:i])
			tail = i + 1
		i += 1

# TODO: find a way to get file text from index OR improve current approach
def str_from_file(filename, start, end):
	with open(filename, 'r') as file:
		file.seek(start)
		return file.read(end - start)

# Builder
def generate_register_header(env, scripts, target):
	defs = parse_definitions(scripts, env['src'])
	write_register_header(defs, env['src'], target)


def parse_definitions(scripts, src):
	defs = {}
	for script in scripts:
		defs |= {script: parse_header(script, src)}

	return defs


def parse_header(filename, src):
	index = clang.cindex.Index.create()
	translation_unit = index.parse(filename, args=[f'-I{src}'], options=clang.cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD)

	if not translation_unit:
		raise Exception("Error: Failed to parse the translation unit!")

	data = extract_methods_and_fields(translation_unit)
	return data


def extract_methods_and_fields(translation_unit):

	classes = []
	found_classes = []
	macros = []
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

	#TODO: better class definition type code
	def parse_cursor(cursor):
		match cursor.kind:
			case clang.cindex.CursorKind.CLASS_DECL:
				found_classes.append(cursor)

			case clang.cindex.CursorKind.MACRO_INSTANTIATION:
				if cursor.spelling in KEYWORDS:
					macros.append(cursor)
				
				elif cursor.spelling.startswith('GEXPORT_'):
					macros.append(cursor)
					
				elif cursor.spelling in ['GCLASS', 'GVIRTUAL_CLASS', 'GABSTRACT_CLASS']:
					found_classes.append(cursor)
					
		for child in cursor.get_children():
			parse_cursor(child)
	

	parse_cursor(translation_unit.cursor)

	found_class = sorted(found_classes, key=lambda x: x.extent.start.offset, reverse=True)	

	def add_class(cursor, macros):
		if len(macros) > 1:
			raise Exception(f'Incorrect usage of GCLASS at <{macros[1].location.file.name}>:{macros[1].location.line}:{macros[1].location.column}')
		
		for macro in macros:
			classes.append((cursor, ''.join([token.spelling for token in list(macro.get_tokens())[4:-1]]), macro.spelling[1:])) # Temporary base name resolution

	collapse_list(found_class, lambda x: x.kind == clang.cindex.CursorKind.CLASS_DECL, add_class)
		
	parsed_classes = {}
	for cursor, base, type in classes:
		class_defs = {
			'base' : base,
			'type' : type,
			'methods' : [],
			'properties' : [],
			'signals' : [],
			'groups' : set(),
			'subgroups' : set(),
			'enum_constants' : {},
			'constants' : [],
			'bitfields' : {}}
		child_cursors = []
		parse_class(cursor, child_cursors)
		group, subgroup = '', ''
		start, end = cursor.extent.start.offset, cursor.extent.end.offset
		class_macros = sorted([m for m in macros if start < m.extent.start.offset < end] + child_cursors, key=lambda x: x.extent.start.offset)

		def process_macros(item, macros, properties):
			nonlocal group
			nonlocal subgroup
			for macro in macros:
				if macro.spelling.startswith('GEXPORT_'):
					properties |= {
						'hint' : 'PROPERTY_HINT_' + macro.spelling[8:],
						# (len(macro.spelling) + 1, -1) - offsets to get body of GEXPORT_***(***) macro
						'hint_string' : str_from_file(macro.extent.start.file.name, macro.extent.start.offset + len(macro.spelling) + 1, macro.extent.end.offset - 1)
						}
					continue

				match macro.spelling:
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

						# Maybe unneeded
						if item.type.spelling[-1] == ')':
							raise Exception(f'Bitfield must be named enum <{macro.location.file.name}>:{macro.location.line}:{macro.location.column}')

						properties['enum_type'] = 'bitfields'

					case 'GSIGNAL':
						#(8, -1) - offsets to get body or macro GSIGNAL(*****)
						macro_args = re.split(r',\s*(?![^{}]*\}|[^<>]*>|[^\(\)]*\))', str_from_file(macro.extent.start.file.name, macro.extent.start.offset + 8, macro.extent.end.offset - 1))
						name = macro_args[0]
						args = []
						for arg in macro_args[1:]:
							idx = arg.rfind(' ')
							if idx == -1:
								args.append(('', arg))
							else:
								args.append((arg[:idx], arg[idx+1:]))
							
						class_defs['signals'].append((name, args))

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
							# Must be a better way of getting default method arguments
							'args' : [(arg.type.spelling, arg.spelling, ''.join([''.join([token.spelling for token in child.get_tokens()]) for child in arg.get_children()])) for arg in item.get_arguments()],
							'is_static' : item.is_static_method()}

					process_macros(item, macros, properties)

					if properties != None:
						class_defs['methods'].append(properties)

				case clang.cindex.CursorKind.ENUM_DECL:
					properties = {'enum_type' : 'enum_constants'}
					properties['list'] = [enum.spelling for enum in item.get_children() if enum.kind == clang.cindex.CursorKind.ENUM_CONSTANT_DECL]

					process_macros(item, macros, properties)

					if item.type.spelling[-1] != ')':	# check for unnamed enum
						class_defs[properties['enum_type']][item.type.spelling] = properties['list']
					else:
						class_defs['constants'] += properties['list']

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
					process_macros(item, macros, properties)

					name = ("" if group == "" else group.lower().replace(" ", "") + "_") + ("" if subgroup == "" else subgroup.lower().replace(" ", "") + "_") + item.spelling
					properties |= {'name': name}

					class_defs['properties'].append(properties)

			return item

						
		collapse_list(class_macros, lambda x: x.kind != clang.cindex.CursorKind.MACRO_INSTANTIATION, apply_macros)
		#print(json.dumps(class_defs, sort_keys=True, indent=2, default=lambda x: x if not isinstance(x, set) else list(x)))
		parsed_classes[cursor.spelling] = class_defs

	return parsed_classes


def write_register_header(defs, src, target):		
	#print(json.dumps(defs, sort_keys=True, indent=2, default=lambda x: x if not isinstance(x, set) else list(x)))
	
	header = ''
	header_register = 'inline void register_script_classes() {\n'
	header_binds = ''

	for file, classes in defs.items():
		header += f'#include "{os.path.relpath(file, src)}"\n'
	
		for class_name, content in classes.items():
			header_register += f"	GDREGISTER_{content['type']}({class_name});\n"

			bind = ['']
			outside_bind = ''
			
			#Groups/subgroups declarations
			for group, name in content['groups']:
				bind.append(f'	ADD_GROUP("{group}", "{name}");')

			bind.append('') if bind[-1] != '' else None

			for group, name in content['subgroups']:
				bind.append(f'	ADD_SUBGROUP("{group}", "{name}");')

			bind.append('') if bind[-1] != '' else None

			for method in content['methods']:
				#TODO: refer to "Generate _bind_methods"
				args = ''.join([f', "{argname}"' if argname != '' else '' for argtype, argname, _ in method['args']])
				defvals = ''.join([', ' + f'DEFVAL({defval})' for _, _, defval in method['args'] if defval != ''])

				bind.append((f'	ClassDB::bind_static_method("{class_name}", ' if method['is_static'] else '	ClassDB::bind_method(') + f'D_METHOD("{method["name"]}"{args}), &{class_name}::{method["name"]}{defvals});')


			bind.append('') if bind[-1] != '' else None

			for prop in content['properties']:
				bind.append(f'	ADD_PROPERTY(PropertyInfo(GetTypeInfo<{prop["type"]}>::VARIANT_TYPE, "{prop["name"]}", {prop["hint"]}, "{prop["hint_string"]}"), "{prop["setter"]}", "{prop["getter"]}");')

			bind.append('') if bind[-1] != '' else None

			for signal_name, args in content['signals']:
				args_str = ''.join([f', PropertyInfo(GetTypeInfo<{arg_type if arg_type != "" else "Variant"}>::VARIANT_TYPE, "{arg_name}")' for arg_type, arg_name in args])
				bind.append(f'	ADD_SIGNAL(MethodInfo("{signal_name}"{args_str}));')

			bind.append('') if bind[-1] != '' else None

			for enum, consts in content['enum_constants'].items():
				#TODO: generate inside class header
				outside_bind += f'VARIANT_ENUM_CAST({enum});'
				for const in consts:
					bind.append(f'	BIND_ENUM_CONSTANT({const});')

			bind.append('') if bind[-1] != '' else None

			for enum, consts in content['bitfields'].items():
				#TODO: generate inside class header
				outside_bind += f'VARIANT_BITFIELD_CAST({enum});'
				for const in consts:
					bind.append(f'	BIND_BITFIELD_FLAG({const});')

			bind.append('') if bind[-1] != '' else None

			for const in content['constants']:
				bind.append(f'	BIND_CONSTANT({const});\n')

			bind = f'void {class_name}::_bind_methods() {{\n' + '\n'.join(bind)[1:] + '};\n' + outside_bind + '\n'

			header_binds += bind

	header += '\nusing namespace godot;\n\n'
	header += header_register + '}\n'
	header += header_binds

	with open(target, 'w') as file:
		file.write(header)

