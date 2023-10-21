from SCons.Script import *
import clang.cindex
import os, re


# TODO
#	+ Register class
#	Register abstract class
#	Generate _bind_methods:
#		+ Simple bind
#		+ With args decsription
#		+ With DEFVAL
#		+ Static methods
#		With varargs
#	+- Properties
#	+ Group/subgroup of properties
#	+ Signals
#
#	+ Constants
#	+ Enums
#		Outside of class
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
	csb = CppScriptBuilder(env, 'src/', [str(i) for i in source])
	#TODO: cache generated definitions
	csb.generate_register_header()


def generate_header_emitter(target, source, env):
	return env.File('src/scripts.gen.h'), source

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
class CppScriptBuilder():
	def __init__(	self,
	      		env,
			src='src/',
	      		scripts=[]
			):
	      self.env = env
	      self.src = src
	      self.scripts = scripts



	def generate_register_header(self):
		defs = self.parse_definitions(self.scripts)
		self.write_register_header(defs)


	def parse_definitions(self, scripts):
		defs = {}
		for s in scripts:
			defs |= self.parse_cpp_file(s)

		return defs


	def parse_cpp_file(self, filename):
		index = clang.cindex.Index.create()
		translation_unit = index.parse(filename, args=['-DGDCLASS', '-Isrc'], options=clang.cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD)

		if not translation_unit:
			print("Error: Failed to parse the translation unit!")
			return

		data = self.extract_methods_and_fields(translation_unit)
		return data
	def extract_methods_and_fields(self, translation_unit):

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
					found_classes.append((cursor, None))

				case clang.cindex.CursorKind.MACRO_INSTANTIATION:
					if cursor.spelling in KEYWORDS:
						macros.append(cursor)
					
					if cursor.spelling.startswith('GEXPORT_'):
						macros.append(cursor)
						
					match cursor.spelling:
						case 'GCLASS':
							found_classes.append((cursor, 'CLASS'))
						case 'GVIRTUAL_CLASS':
							found_classes.append((cursor, 'VIRTUAL_CLASS'))
						case 'GABSTRACT_CLASS':
							found_classes.append((cursor, 'ABSTRACT_CLASS'))

						case 'GPROPERTY':
							pass
						
			for child in cursor.get_children():
				parse_cursor(child)
		

		parse_cursor(translation_unit.cursor)

		found_class = sorted(found_classes, key=lambda x: x[0].extent.start.offset, reverse=True)	

		def add_class(cursor, macros):
			if len(macros) > 1:
				raise Exception(f'Incorrect usage of GCLASS at <{macros[1].location.file.name}>:{macros[1].location.line}:{macros[1].location.column}')
			
			for macro in macros:
				classes.append((cursor[0], ''.join([token.spelling for token in list(macro[0].get_tokens())[4:-1]]), macro[1])) # Temporary base name resolution

		collapse_list(found_class, lambda x: x[0].kind == clang.cindex.CursorKind.CLASS_DECL, add_class)
			
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


	def write_register_header(self, defs):		
		#print(json.dumps(defs, sort_keys=True, indent=2, default=lambda x: x if not isinstance(x, set) else list(x)))
		"""
		class_defs = {
				'base' : base,
				'methods' : [],
				'properties' : [],
				'signals' : [],
				'groups' : set(),
				'subgroups' : set(),
				'enum_constants' : {},
				'constants' : [],
				'bitfields' : {}}
		"""

		header = ''
		# Generate include headers
		for file in self.scripts:
			header += f'#include "{os.path.relpath(file, self.src)}"\n'
		
		header += '\nusing namespace godot;\n\n'
		# Generate register_classes function
		register_classes_str = 'inline void register_script_classes() {\n'
		register_classes_str += ''.join([f"	GDREGISTER_{props['type']}({name});\n" for name, props in defs.items()])
		register_classes_str += '}\n'
		header += register_classes_str
		# Generate _bind_methods for each class
		for class_name, content in defs.items():
			bind = f'void {class_name}::_bind_methods() {{\n'
			outside_bind = ''
			
			#Groups/subgroups declarations
			for group, name in content['groups']:
				bind += f'	ADD_GROUP("{group}", "{name}");\n'

			bind += '\n'

			for group, name in content['subgroups']:
				bind += f'	ADD_SUBGROUP("{group}", "{name}");\n'

			bind += '\n'

			for method in content['methods']:
				#TODO: refer to "Generate _bind_methods"
				args = ''.join([f', "{argname}"' if argname != '' else '' for argtype, argname, _ in method['args']])
				defvals = ''.join([', ' + f'DEFVAL({defval})' for _, _, defval in method['args'] if defval != ''])

				bind += (f'	ClassDB::bind_static_method("{class_name}", ' if method['is_static'] else '	ClassDB::bind_method(') + f'D_METHOD("{method["name"]}"{args}), &{class_name}::{method["name"]}{defvals});\n'


			bind += '\n'

			for prop in content['properties']:
				bind += f'	ADD_PROPERTY(PropertyInfo(GetTypeInfo<{prop["type"]}>::VARIANT_TYPE, "{prop["name"]}", {prop["hint"]}, "{prop["hint_string"]}"), "{prop["setter"]}", "{prop["getter"]}");\n'

			bind += '\n'

			for signal_name, args in content['signals']:
				args_str = ''.join([f', PropertyInfo(GetTypeInfo<{arg_type if arg_type != "" else "Variant"}>::VARIANT_TYPE, "{arg_name}")' for arg_type, arg_name in args])
				bind += f'	ADD_SIGNAL(MethodInfo("{signal_name}"{args_str}));\n'

			bind += '\n'

			for enum, consts in content['enum_constants'].items():
				#TODO: generate inside class header
				outside_bind += f'VARIANT_ENUM_CAST({enum});\n'
				for const in consts:
					bind += f'	BIND_ENUM_CONSTANT({const});\n'

			bind += '\n'

			for enum, consts in content['bitfields'].items():
				#TODO: generate inside class header
				outside_bind += f'VARIANT_BITFIELD_CAST({enum});\n'
				for const in consts:
					bind += f'	BIND_BITFIELD_FLAG({const});\n'

			bind += '\n'

			for const in content['constants']:
				bind += f'	BIND_CONSTANT({const});\n'

			bind += '};\n'
			bind += outside_bind + '\n'

			header += bind

		#print(json.dumps(defs, sort_keys=True, indent=2, default=lambda x: x if not isinstance(x, set) else list(x)))
		with open(os.path.join(self.src, 'scripts.gen.h'), 'w') as file:
			file.write(header)

