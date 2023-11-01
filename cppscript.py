from SCons.Script import *
import clang.cindex
import pcpp
import os, sys, json



KEYWORDS = ['GPROPERTY', 'GGROUP', 'GSUBGROUP', 'GBITFIELD', 'GSIGNAL', 'GRPC', 'GVARARG', 'GIGNORE']
VIRTUAL_METHODS = ['_enter_tree', '_exit_tree', '_input', '_unhandled_input', '_unhandled_key_input', '_process', '_physics_process']

# Helpers
class CppScriptException(Exception):
	pass


def generate_header(target, source, env):
	index = clang.cindex.Index.create()
	try:
		sourcesigs, sources = target[0].get_stored_info().binfo.bsourcesigs, target[0].get_stored_info().binfo.bsources
		cached_defs = load_defs_json(env['defs_file'])

		new_defs = {str(s) : (cached_defs[str(s)] if str(s) in sources and s.get_csig() == sourcesigs[sources.index(str(s))].csig and str(s) in cached_defs.keys() else parse_header(index, s, env['src'])) for s in source}

	except AttributeError:
		new_defs = {str(s) : parse_header(index, s, env['src']) for s in source}

	try:
		write_register_header(new_defs, env['src'], str(target[0]))

		with open(env['defs_file'], 'w') as file:
			json.dump(new_defs, file, indent=2, default=lambda x: x if not isinstance(x, set) else list(x))

	except CppScriptException as e:
		print(f'\n{e}\n', file=sys.stderr)
		return 1


def generate_header_emitter(target, source, env):
	return env.File(env['gen_header']), source

def collapse_list(list, key, action):
	tail = 0
	for i in range(len(list)):
		if key(list[i]) == True:
			action(list[i], list[tail:i])
			tail = i + 1
	return list[tail:]


def get_pair_arglist(args, default_left):
	pairs = []
	for arg in args:
		idx = arg.rfind(' ')
		if idx == -1:
			pairs.append((default_left, arg))
		else:
			pairs.append((arg[:idx], arg[idx+1:]))
	return pairs


def find_default_arg(file, arg):
	arg_def = str_from_file(arg.extent.start.file.name, arg.extent.start.offset, arg.extent.end.offset)
	for token in arg.get_tokens():
		if token.spelling == '=':
			return str_from_file(file, token.extent.end.offset, arg.extent.end.offset).lstrip()

	return ''


def load_defs_json(path):
	try:
		with open(path, 'r') as file:
			return json.load(file)
	except Exception:
		return {}


def Raise(e):
	raise e


def str_from_file(file, start, end):
	return file[start:end]


def get_macro_body(file, macro):
	return str_from_file(file, macro.extent.start.offset + len(macro.spelling) + 1, macro.extent.end.offset - 1)


def GlobRecursive(path, pattern, **kwargs):
	found = []
	for root, dirs, files in os.walk(path):
		found += Glob(root + '/' + pattern, **kwargs)
	
	return found


def get_macro_args(file, macro):
	p = pcpp.Preprocessor()
	n, args, pos = p.collect_args(list(p.parsegen(str_from_file(file, macro.extent.start.offset + len(macro.spelling), macro.extent.end.offset))))
	return [''.join([i.value for i in arg]) for arg in args]


def group_name(name):
	return '' if name == '' else (name.lower().replace(" ", "") + "_")

 
# Builder
def parse_header(index, scons_file, src):
	file = scons_file.get_text_contents()
	translation_unit = index.parse(str(scons_file), args=[f'-I{src}', '-Isrc'], unsaved_files=[(str(scons_file), file)], options=clang.cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD)

	if not translation_unit:
		raise CppScriptException("{str(scons_file)}: failed to create translation unit")

	classes = []
	found_classes = []
	macros = []
	def parse_class(parent, class_cursors):
		for cursor in parent.get_children():
			match cursor.kind:
				case clang.cindex.CursorKind.CXX_METHOD:
					# Temporarily do not register virtual methods
					if cursor.access_specifier == clang.cindex.AccessSpecifier.PUBLIC and not cursor.is_virtual_method():
						class_cursors.append(cursor)
					
				case clang.cindex.CursorKind.FIELD_DECL:
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
					
				elif cursor.spelling in ['GCLASS', 'GVIRTUAL_CLASS', 'GABSTRACT_CLASS']:
					found_classes.append(cursor)
					
		for child in cursor.get_children():
			parse_cursor(child)
	

	parse_cursor(translation_unit.cursor)

	found_class = sorted(found_classes, key=lambda x: x.extent.start.offset, reverse=True)	

	def add_class(cursor, macros):
		if len(macros) > 1:
			raise CppScriptException('{}:{}:{}: error: repeated class macro for a class at {}:{}'
		       	.format(str(scons_file), macros[1].location.line, macros[1].location.column, macros[1].spelling, cursor.location.line, cursor.location.column))

		
		for macro in macros:
			classes.append((cursor, get_macro_args(file, macro)[1], macro.spelling[1:]))


	collapse_list(found_class, lambda x: x.kind == clang.cindex.CursorKind.CLASS_DECL, add_class)
		
	parsed_classes = {}
	for cursor, base, type in classes:
		class_defs = {
			'base' : base,
			'type' : type,
			'methods' : [],
			'properties' : [],
			'signals' : [],
			'enum_constants' : {},
			'constants' : [],
			'bitfields' : {}
			}
		child_cursors = []
		parse_class(cursor, child_cursors)
		group, subgroup = '', ''
		start, end = cursor.extent.start.offset, cursor.extent.end.offset
		class_macros = sorted([m for m in macros if start < m.extent.start.offset < end] + child_cursors, key=lambda x: x.extent.start.offset)

		def process_macros(item, macros, properties, is_ignored=False):
			nonlocal group
			nonlocal subgroup
			for macro in macros:
				match macro.spelling:
					case 'GPROPERTY':
						if item.kind != clang.cindex.CursorKind.FIELD_DECL:
							raise CppScriptException('{}:{}:{}: error: incorrect {} macro usage on definition at {}:{}: must be data member'
		       					.format(str(scons_file), macro.location.line, macro.location.column, macro.spelling, item.location.line, item.location.column))

						args = get_macro_args(file, macro)
						if len(args) < 2:
							raise CppScriptException('{}:{}:{}: error: incorrect {} macro usage: must be at least 2 arguments: setter and getter'
		       					.format(str(scons_file), macro.location.line, macro.location.column, macro.spelling))
					
						properties |= {
								'setter' : args[0],
								'getter' : args[1],
								'hint' : 'PROPERTY_HINT_' + args[2].upper() if len(args) > 2 else 'PROPERTY_HINT_NONE',
								'hint_string' : args[3] if len(args) > 3 else '""'
								}
						is_ignored = False

					case 'GGROUP':
						group = get_macro_body(file, macro)
						subgroup = ''

					case 'GSUBGROUP':
						subgroup = get_macro_body(file, macro)

					case 'GBITFIELD':
						if item.kind != clang.cindex.CursorKind.ENUM_DECL:
							raise CppScriptException('{}:{}:{}: error: incorrect {} macro usage on definition at {}:{}: must be enum'
		       					.format(str(scons_file), macro.location.line, macro.location.column, macro.spelling, item.location.line, item.location.column))

						if item.type.spelling[-1] == ')':
								raise CppScriptException('{}:{}:{}: error: enum at {}:{} must be named'
		       						.format(str(scons_file), macro.location.line, macro.location.column, item.location.line, item.location.column))
						
						properties['enum_type'] = 'bitfields'

					case 'GSIGNAL':
						macro_args = get_macro_args(file, macro)
						name = macro_args[0]
						args = get_pair_arglist(macro_args[1:], '')
						class_defs['signals'].append((name, args))

					case 'GRPC':
						if item.kind != clang.cindex.CursorKind.CXX_METHOD:
							raise CppScriptException('{}:{}:{}: error: incorrect {} macro usage on definition at {}:{}: must be member function'
		       					.format(str(scons_file), macro.location.line, macro.location.column, macro.spelling, item.location.line, item.location.column))

						macro_args = get_macro_args(file, macro)
						rpc_mode, transfer_mode, call_local, channel = None, None, None, None

						if len(macro_args) != 0 and macro_args[-1].isnumeric():
							if len(macro_args) < 3:
								raise CppScriptException('{}:{}:{}: error: channel id must come with explicit rpc_mode and transfer_mode'
			       					.format(str(scons_file), macro.location.line, macro.location.column))

							parse_args = macro_args[:-1]
							channel = macro_args[-1]
						else:
							parse_args = macro_args

						for arg in macro_args:
							match arg:
								case ('any_peer' | 'authority') as mode:
									rpc_mode = mode.upper() if rpc_mode == None else Raise(
									CppScriptException('{}:{}:{}: error: duplicate rpc mode keyword usage'
		       							.format(str(scons_file), macro.location.line, macro.location.column)))


								case ('reliable' | 'unreliable' | 'unreliable_ordered') as mode:
									transfer_mode = mode.upper() if transfer_mode == None else Raise(
									CppScriptException('{}:{}:{}: error: duplicate transfer mode keyword usage'
		       							.format(str(scons_file), macro.location.line, macro.location.column)))


								case ('call_local' | 'call_remote') as mode:
									mode = 'true' if mode == 'call_local' else 'false'
									call_local = mode if call_local == None else Raise(
									CppScriptException('{}:{}:{}: error: duplicate call mode keyword usage'
		       							.format(str(scons_file), macro.location.line, macro.location.column)))


						rpc_config = {	'rpc_mode' : 'RPC_MODE_' + rpc_mode if rpc_mode != None else 'RPC_MODE_AUTHORITY',
								'transfer_mode' : 'TRANSFER_MODE_' + transfer_mode if transfer_mode != None else 'TRANSFER_MODE_UNRELIABLE',
		    						'call_local' : call_local if call_local != None else 'false',
		    						'channel' : channel if channel != None else '0'}
						
						properties['rpc_config'] = rpc_config 

					case 'GVARARG':
						if item.kind != clang.cindex.CursorKind.CXX_METHOD:
							raise CppScriptException('{}:{}:{}: error: incorrect {} macro usage on definition at {}:{}: must be member function'
		       					.format(str(scons_file), macro.location.line, macro.location.column, macro.spelling, item.location.line, item.location.column))

						varargs = get_pair_arglist(get_macro_args(file, macro), 'Variant')
						properties['is_vararg'] = True
						properties['args'] = varargs
					
					case 'GIGNORE':
						is_ignored = True

			return not is_ignored


		def apply_macros(item, macros):
			nonlocal group
			nonlocal subgroup
			properties = None
			match item.kind:
				case clang.cindex.CursorKind.CXX_METHOD:
					if item.spelling not in VIRTUAL_METHODS and not item.is_virtual_method(): # Do not register virtual temporary
						properties = {
							'name' : item.spelling,
							'bind_name' : item.spelling,
							'return' : item.result_type.spelling,
							# Must be a better way of getting default method arguments
							'args' : [(arg.type.spelling, arg.spelling, find_default_arg(file, arg)) for arg in item.get_arguments()],
							'is_static' : item.is_static_method(),
							'is_vararg': False,
							'rpc_config' : None
							}

						if process_macros(item, macros, properties):

							if properties != None:
								class_defs['methods'].append(properties)

				case clang.cindex.CursorKind.ENUM_DECL:
					properties = {'enum_type' : 'enum_constants'}
					properties['list'] = [enum.spelling for enum in item.get_children() if enum.kind == clang.cindex.CursorKind.ENUM_CONSTANT_DECL]

					if process_macros(item, macros, properties):

						if item.type.spelling[-1] != ')':	# check for named enum
							class_defs[properties['enum_type']][item.type.spelling] = properties['list']
						else:
							class_defs['constants'] += properties['list']

				case clang.cindex.CursorKind.FIELD_DECL:
					properties = {
						'name' : '',
						'group' : '',
						'subgroup' : '',
						'setter' : '',
						'getter' : '',
						'hint' : 'PROPERTY_HINT_NONE',
						'hint_string' : '',
						'is_static' : item.is_static_method()
						}
					if process_macros(item, macros, properties, True):
						properties |= { 'name': item.spelling,
								'group' : group,
								'subgroup' : subgroup
								}

						class_defs['properties'].append(properties)

			return item

						
		leftover = collapse_list(class_macros, lambda x: x.kind != clang.cindex.CursorKind.MACRO_INSTANTIATION, apply_macros)
		for macro in leftover:
			if macro.spelling not in ['GSIGNAL', 'GGROUP', 'GSUBGROUP']:
				raise CppScriptException('{}:{}:{}: error: macro without target member'
		   		.format(str(scons_file), macro.location.line, macro.location.column))
		process_macros(None, leftover, None)


		parsed_classes[cursor.spelling] = class_defs

	return parsed_classes


def write_register_header(defs, src, target):		
	scripts_header = ''
	header_register = 'inline void register_script_classes() {\n'
	header_defs = ''

	for file, classes in defs.items():
		if len(classes) != 0:
			scripts_header += '#include <{}>\n'.format(os.path.relpath(file, src).replace('\\', '/'))

		for class_name, content in classes.items():
			header_register += f"	GDREGISTER_{content['type']}({class_name});\n"

		for class_name, content in classes.items():
			Hmethod, Hstatic_method, Hvaragr_method, Hprop, Hsignal, Henum, Hbitfield, Hconst = '', '', '', '', '', '', '', ''
			outside_bind = ''
			header_rpc_config = ''
			methods_list = [method['bind_name'] for method in content['methods']]

			for method in content['methods']:
				if not method['is_vararg']:
					args = ''.join([f', "{argname}"' if argname != '' else '' for argtype, argname, _ in method['args']])
					defvals = ''.join([f', DEFVAL({defval})' for _, _, defval in method['args'] if defval != ''])
					if method['is_static']:
						Hstatic_method += f'	ClassDB::bind_static_method("{class_name}", D_METHOD("{method["bind_name"]}"{args}), &{class_name}::{method["name"]}{defvals});\n'
					else:
						Hmethod += f'	ClassDB::bind_method(D_METHOD("{method["bind_name"]}"{args}), &{class_name}::{method["name"]}{defvals});\n'

					if method['rpc_config'] != None:
						header_rpc_config += f"""	{{
		Dictionary opts;
		opts["rpc_mode"] = MultiplayerAPI::{method['rpc_config']['rpc_mode']};
		opts["transfer_mode"] = MultiplayerPeer::{method['rpc_config']['transfer_mode']};
		opts["call_local"] = {method['rpc_config']['call_local']};
		opts["channel"] = {method['rpc_config']['channel']};
		rpc_config("{method["name"]}", opts);
	}}
"""
				else:
					args_list = '\n'.join([f'		mi.arguments.push_back(PropertyInfo(GetTypeInfo<{type}>::VARIANT_TYPE, "{name}"));' for type, name in method['args']])

					Hvaragr_method += f"""	{{
		MethodInfo mi;
		mi.name = "{method["name"]}";
""" + args_list + f"""
		ClassDB::bind_vararg_method(METHOD_FLAGS_DEFAULT, "{method["bind_name"]}", &{class_name}::{method["name"]}, mi);
	}}
"""
			prev_group, prev_subgroup = '', ''
			for prop in content['properties']:
				if prop['getter'] not in methods_list:
					Hmethod += f'	ClassDB::bind_method(D_METHOD("{prop["getter"]}"), &{class_name}::_cppscript_getter<&{class_name}::{prop["name"]}>);\n'

				if prop['setter'] not in methods_list:
					Hmethod += f'	ClassDB::bind_method(D_METHOD("{prop["setter"]}", "value"), &{class_name}::_cppscript_setter<&{class_name}::{prop["name"]}>);\n'

				group, subgroup = prop['group'], prop['subgroup']
				group_ = group_name(group)
				if group != '' and group != prev_group:
					Hprop += f'	ADD_GROUP("{group}", "{group_}");\n'
					prev_group = group

				subgroup_ = group_name(subgroup)
				if subgroup != '' and subgroup != prev_subgroup:
					Hprop += f'	ADD_SUBGROUP("{subgroup}", "{group_}{subgroup_}");\n'
					prev_subgroup = subgroup

				prop_name = group_ + subgroup_ + prop['name']
				Hprop += f'		ADD_PROPERTY(PropertyInfo(GetTypeInfo<decltype({class_name}::{prop["name"]})>::VARIANT_TYPE, "{prop_name}", {prop["hint"]}, {prop["hint_string"]}), "{prop["setter"]}", "{prop["getter"]}");\n'

			for signal_name, args in content['signals']:
				args_str = ''.join([f', PropertyInfo(GetTypeInfo<{arg_type if arg_type != "" else "Variant"}>::VARIANT_TYPE, "{arg_name}")' for arg_type, arg_name in args])
				Hsignal += f'	ADD_SIGNAL(MethodInfo("{signal_name}"{args_str}));\n'

			for enum, consts in content['enum_constants'].items():
				outside_bind += f'VARIANT_ENUM_CAST({enum});\n'
				for const in consts:
					Henum += f'	BIND_ENUM_CONSTANT({const});\n'

			for enum, consts in content['bitfields'].items():
				outside_bind += f'VARIANT_BITFIELD_CAST({enum});\n'
				for const in consts:
					Hbitfield += f'	BIND_BITFIELD_FLAG({const});\n'

			for const in content['constants']:
				Hconst += f'	BIND_CONSTANT({const});\n'

			header_rpc_config = f'void {class_name}::_rpc_config() {{' + ('' if header_rpc_config == '' else '\n') + header_rpc_config + '}\n\n'
			bind_array = [i for i in [Hmethod, Hstatic_method, Hvaragr_method, Hprop, Hsignal, Henum, Hbitfield, Hconst] if i != '']
			header_defs += outside_bind + f'void {class_name}::_bind_methods() {{' + ''.join(['\n\n' + i for i in bind_array]) + '}\n\n' + header_rpc_config

	scripts_header += '\nusing namespace godot;\n\n'
	scripts_header += header_register + '}\n\n'
	scripts_header += header_defs

	with open(target, 'w') as file:
		file.write(scripts_header)

