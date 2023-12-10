from clang.cindex import Index, TranslationUnit, CursorKind, TokenKind, AccessSpecifier
import os, sys, json

if 'NOT_SCONS' not in os.environ.keys():
	from SCons.Script import Glob
	def GlobRecursive(path, pattern, **kwargs):
		found = []
		for root, dirs, files in os.walk(path):
			if not os.path.basename(root).startswith('.'):
				found += Glob(root + '/' + pattern, **kwargs)
			else:
				dirs[:] = []

		return found


KEYWORDS = ['GPROPERTY', 'GMETHOD', 'GGROUP', 'GSUBGROUP', 'GBITFIELD', 'GSIGNAL', 'GRPC', 'GVARARG', 'GIGNORE']
INIT_LEVELS = ['GINIT_LEVEL_CORE', 'GINIT_LEVEL_SERVERS', 'GINIT_LEVEL_SCENE', 'GINIT_LEVEL_EDITOR']

# Helpers
class CppScriptException(Exception):
	pass

def filename_to_gen_filename(name, src):
	return os.path.join(src, '.gen', os.path.relpath(name.replace('.hpp', '.gen.cpp'), src))


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
	arg_def = str_from_file(file, arg.extent.start.offset, arg.extent.end.offset)
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


def str_from_file(file, start, end):
	return file[start:end]


def get_macro_body(file, macro):
	return str_from_file(file, macro.extent.start.offset + len(macro.spelling) + 1, macro.extent.end.offset - 1)


def get_macro_args(file, macro):
	args_str = get_macro_body(file, macro)

	args = []
	in_quotes, escaped = False, False
	tail, brack_count = 0, 0
	for idx in range(len(args_str)):
		match args_str[idx]:
			case '\\':
				escaped = True
				continue

			case '"':
				if not escaped:
					in_quotes = not in_quotes

			case '(' | '<' | '[' | '{':
				if not in_quotes:
					brack_count += 1

			case ')' | '>' | ']' | '}':
				if not in_quotes:
					brack_count -= 1

			case ',':
				if not in_quotes and brack_count == 0:
					args.append(args_str[tail:idx].strip())
					tail = idx + 1
		escaped = False

	last = args_str[tail:].strip()
	if last != '':
		args.append(last)

	return args


def group_name(name):
	return '' if name == '' else (name.lower().replace(" ", "") + "_")

 
def get_file_scons(scons_file):
	return str(scons_file), scons_file.get_text_contents()


def get_file_cmake(filename):
	with open(filename, 'r') as file:
		filecontent = file.read()

	return filename, filecontent


def is_virtual_method(cursor):
	for token in cursor.get_tokens():
		if (token.kind, token.spelling) in [(TokenKind.IDENTIFIER, "override"), (TokenKind.KEYWORD, "virtual")]:
			return True

	return False


# Builder
def generate_header_emitter(target, source, env):
	return [env.File(env['gen_header'])] + [env.File(filename_to_gen_filename(str(i), env['src'])) for i in source], source


def generate_header(target, source, env):
	index = Index.create()
	try:
		os.remove(os.path.join(env['src'], 'properties.gen.h'))
	except:
		pass

	try:
		try:
			sourcesigs, sources = target[0].get_stored_info().binfo.bsourcesigs, target[0].get_stored_info().binfo.bsources
			cached_defs = load_defs_json(env['defs_file'])

			new_defs = {str(s) : (cached_defs[str(s)]
						if str(s) in sources and s.get_csig() == sourcesigs[sources.index(str(s))].csig and str(s) in cached_defs.keys()
						else parse_and_write_header(index, *get_file_scons(s), env)) for s in source}

		except AttributeError:
			new_defs = {str(s) : parse_and_write_header(index, *get_file_scons(s), env) for s in source}

		write_register_header(new_defs, env['src'], str(target[0]))
		write_property_header(new_defs, os.path.join(env['src'], 'properties.gen.h'))

		with open(env['defs_file'], 'w') as file:
			json.dump(new_defs, file, indent=2, default=lambda x: x if not isinstance(x, set) else list(x))
		
	except CppScriptException as e:
		print(f'\n{e}\n', file=sys.stderr)
		return 1


def generate_header_cmake(target, source, env):
	index = Index.create()
	try:
		os.remove(os.path.join(env['src'], 'properties.gen.h'))
	except:
		pass
	
	try:
		cached_defs = load_defs_json(env['defs_file'])
		new_defs = {str(s) : parse_and_write_header(index, *get_file_cmake(s), env) for s in source}
		
		write_register_header(new_defs, env['src'], str(target[0]))
		write_property_header(new_defs, os.path.join(env['src'], 'properties.gen.h'))

		with open(env['defs_file'], 'w') as file:
			json.dump(new_defs, file, indent=2, default=lambda x: x if not isinstance(x, set) else list(x))
		
	except CppScriptException as e:
		print(f'\n{e}\n', file=sys.stderr)
		return 1
	
	return 0

def parse_header(index, filename, filecontent, src, auto_methods):
	translation_unit = index.parse(filename, args=[f'-I{src}', '-Isrc', '-DGDCLASS'], unsaved_files=[(filename, filecontent)], options=TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD)

	if not translation_unit:
		raise CppScriptException("{filename}: failed to create translation unit")

	classes_and_Gmacros = []
	keyword_macros = []
	def parse_class(parent, class_cursors):
		for cursor in parent.get_children():
			match cursor.kind:
				case CursorKind.CXX_METHOD:
					if cursor.access_specifier == AccessSpecifier.PUBLIC:
						class_cursors.append(cursor)
					
				case CursorKind.FIELD_DECL:
					class_cursors.append(cursor)

				case CursorKind.ENUM_DECL:
					if cursor.access_specifier == AccessSpecifier.PUBLIC:
						class_cursors.append(cursor)


	def parse_cursor(parent):
		for cursor in parent.get_children():
			match cursor.kind:
				case CursorKind.CLASS_DECL:
					classes_and_Gmacros.append(cursor)

				case CursorKind.MACRO_INSTANTIATION:
					if cursor.spelling in KEYWORDS:
						keyword_macros.append(cursor)

					elif cursor.spelling in INIT_LEVELS:
						keyword_macros.append(cursor)

					elif cursor.spelling in ['GCLASS', 'GVIRTUAL_CLASS', 'GABSTRACT_CLASS']:
						classes_and_Gmacros.append(cursor)

				case _:
					parse_cursor(cursor)

	parse_cursor(translation_unit.cursor)
	found_class = sorted(classes_and_Gmacros, key=lambda x: x.extent.start.offset, reverse=True)	
	classes = []
	def add_class(cursor, macros):
		if len(macros) > 1:
			wrong_macro = macros[-2]
			raise CppScriptException('{}:{}:{}: error: repeated class macro for "{}" class defined at {}:{}'
			.format(filename, wrong_macro.location.line, wrong_macro.location.column, cursor.spelling, cursor.location.line, cursor.location.column))

		
		for macro in macros:
			classes.append((cursor, get_macro_args(filecontent, macro)[1], macro.spelling[1:]))


	collapse_list(found_class, lambda x: x.kind == CursorKind.CLASS_DECL, add_class)
		
	parsed_classes = {}
	for cursor, base, type in classes:
		class_defs = {
			'class_name' : cursor.spelling,
			'base' : base,
			'type' : type,
			'init_level' : 'SCENE',
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
		class_macros = sorted([m for m in keyword_macros if start < m.extent.start.offset < end] + child_cursors, key=lambda x: x.extent.start.offset)

		def process_macros(item, macros, properties, is_ignored=False):
			nonlocal group
			nonlocal subgroup
			for macro in macros:
				if macro.spelling in INIT_LEVELS:
					class_defs['init_level'] = macro.spelling[12:]

				match macro.spelling:
					case 'GMETHOD':
						if item.kind != CursorKind.CXX_METHOD:
							raise CppScriptException('{}:{}:{}: error: incorrect {} macro usage on definition at {}:{}: must be member function'
							.format(filename, macro.location.line, macro.location.column, macro.spelling, item.location.line, item.location.column))

						is_ignored = False

					case 'GPROPERTY':
						if item.kind != CursorKind.FIELD_DECL:
							raise CppScriptException('{}:{}:{}: error: incorrect {} macro usage on definition at {}:{}: must be data member'
							.format(filename, macro.location.line, macro.location.column, macro.spelling, item.location.line, item.location.column))

						args = get_macro_args(filecontent, macro)
						if len(args) < 2:
							raise CppScriptException('{}:{}:{}: error: incorrect {} macro usage: must be at least 2 arguments: setter and getter'
							.format(filename, macro.location.line, macro.location.column, macro.spelling))
					
						properties |= {
								'setter' : args[0],
								'getter' : args[1],
								'hint' : 'PROPERTY_HINT_' + args[2].upper() if len(args) > 2 else None,
								'hint_string' : args[3] if len(args) > 3 else '""'
								}
						is_ignored = False

					case 'GGROUP':
						group = get_macro_body(filecontent, macro)
						subgroup = ''

					case 'GSUBGROUP':
						subgroup = get_macro_body(filecontent, macro)

					case 'GBITFIELD':
						if item.kind != CursorKind.ENUM_DECL:
							raise CppScriptException('{}:{}:{}: error: incorrect {} macro usage on definition at {}:{}: must be enum'
							.format(filename, macro.location.line, macro.location.column, macro.spelling, item.location.line, item.location.column))

						if item.type.spelling[-1] == ')':
								raise CppScriptException('{}:{}:{}: error: enum at {}:{} must be named'
								.format(filename, macro.location.line, macro.location.column, item.location.line, item.location.column))
						
						properties['enum_type'] = 'bitfields'

					case 'GSIGNAL':
						macro_args = get_macro_args(filecontent, macro)
						name = macro_args[0]
						args = get_pair_arglist(macro_args[1:], 'Variant')
						class_defs['signals'].append((name, args))

					case 'GRPC':
						if item.kind != CursorKind.CXX_METHOD:
							raise CppScriptException('{}:{}:{}: error: incorrect {} macro usage on definition at {}:{}: must be member function'
							.format(filename, macro.location.line, macro.location.column, macro.spelling, item.location.line, item.location.column))

						macro_args = get_macro_args(filecontent, macro)
						rpc_mode, transfer_mode, call_local, channel = None, None, None, None

						if len(macro_args) != 0 and macro_args[-1].isnumeric():
							if len(macro_args) < 3:
								raise CppScriptException('{}:{}:{}: error: channel id must come with explicit rpc_mode and transfer_mode'
								.format(filename, macro.location.line, macro.location.column))

						for arg in macro_args:
							match arg:
								case ('any_peer' | 'authority') as mode:
									if rpc_mode != None:
										raise CppScriptException('{}:{}:{}: error: duplicate rpc mode keyword usage'
										.format(filename, macro.location.line, macro.location.column)) 

									rpc_mode = mode.upper()


								case ('reliable' | 'unreliable' | 'unreliable_ordered') as mode:
									if transfer_mode != None:
										raise CppScriptException('{}:{}:{}: error: duplicate transfer mode keyword usage'
										.format(filename, macro.location.line, macro.location.column))

									transfer_mode = mode.upper()


								case ('call_local' | 'call_remote') as mode:
									mode = 'true' if mode == 'call_local' else 'false'
									if call_local != None:
										raise CppScriptException('{}:{}:{}: error: duplicate call mode keyword usage'
										.format(filename, macro.location.line, macro.location.column))

									call_local = mode

								case _:
									if not arg.isnumeric():
										raise CppScriptException('{}:{}:{}: error: "{}" is not a keyword or channel id'
										.format(filename, macro.location.line, macro.location.column, arg))

									if channel != None:
										raise CppScriptException('{}:{}:{}: error: duplicate channel id usage'
										.format(filename, macro.location.line, macro.location.column))

									channel = arg


						rpc_config = {	'rpc_mode' : 'RPC_MODE_' + rpc_mode if rpc_mode != None else 'RPC_MODE_AUTHORITY',
								'transfer_mode' : 'TRANSFER_MODE_' + transfer_mode if transfer_mode != None else 'TRANSFER_MODE_UNRELIABLE',
		    						'call_local' : call_local if call_local != None else 'false',
		    						'channel' : channel if channel != None else '0'}
						
						properties['rpc_config'] = rpc_config 

					case 'GVARARG':
						if item.kind != CursorKind.CXX_METHOD:
							raise CppScriptException('{}:{}:{}: error: incorrect {} macro usage on definition at {}:{}: must be member function'
							.format(filename, macro.location.line, macro.location.column, macro.spelling, item.location.line, item.location.column))

						properties['varargs'] = get_pair_arglist(get_macro_args(filecontent, macro), 'Variant')
					
					case 'GIGNORE':
						is_ignored = True

			return not is_ignored


		def apply_macros(item, macros):
			nonlocal group
			nonlocal subgroup
			properties = None
			match item.kind:
				case CursorKind.CXX_METHOD:
					is_virtual = is_virtual_method(item)
					properties = {}
					if process_macros(item, macros, properties, (is_virtual and item.spelling.startswith('_')) or not auto_methods):
						properties |= {	'name' : item.spelling,
								'bind_name' : item.spelling,
								'return' : item.result_type.spelling,
								'args' : [(arg.type.spelling, arg.spelling, find_default_arg(filecontent, arg)) for arg in item.get_arguments()],
								'is_static' : item.is_static_method(),
								'is_virtual' : is_virtual
								}
						class_defs['methods'].append(properties)

				case CursorKind.ENUM_DECL:
					properties = {'enum_type' : 'enum_constants'}
					properties['list'] = [enum.spelling for enum in item.get_children() if enum.kind == CursorKind.ENUM_CONSTANT_DECL]

					if process_macros(item, macros, properties):

						if item.type.spelling[-1] != ')':	# check for named enum
							class_defs[properties['enum_type']][item.type.spelling] = properties['list']
						else:
							class_defs['constants'] += properties['list']

				case CursorKind.FIELD_DECL:
					properties = {}
					if process_macros(item, macros, properties, True):
						properties |= { 'name': item.spelling,
								'group' : group,
								'subgroup' : subgroup,
								'is_static' : item.is_static_method()
								}

						class_defs['properties'].append(properties)


						
		leftover = collapse_list(class_macros, lambda x: x.kind != CursorKind.MACRO_INSTANTIATION, apply_macros)
		for macro in leftover:
			if macro.spelling not in ['GSIGNAL', 'GGROUP', 'GSUBGROUP']:
				raise CppScriptException('{}:{}:{}: error: macro without target member'
				.format(filename, macro.location.line, macro.location.column))
		process_macros(None, leftover, None)


		parsed_classes[cursor.type.spelling] = class_defs

	return parsed_classes


def parse_and_write_header(index, filename, filecontent, env):
	defs = parse_header(index, filename, filecontent, env['src'], env['auto_methods'])
	write_header(filename, defs, env['src'])
	return defs


def write_header(file, defs, src):
	header_defs = []
	for class_name_full, content in defs.items():
		class_name = content['class_name']
		Hmethod, Hstatic_method, Hvirtual_method, Hvaragr_method, Hprop, Hsignal, Henum, Hbitfield, Hconst = '', '', '', '', '', '', '', '', ''
		outside_bind = ''
		header_rpc_config = ''
		gen_setters, gen_getters = [], []
		property_set_get_defs = ''
		methods_list = [method['bind_name'] for method in content['methods']]

		for method in content['methods']:
			if 'varargs' not in method.keys():
				args = ''.join(f', "{argname}"' if argname != '' else '' for argtype, argname, _ in method['args'])
				defvals = ''.join(f', DEFVAL({defval})' for _, _, defval in method['args'] if defval != '')
				if method['is_static']:
					Hstatic_method += f'\tStaticMethod<&{class_name}::{method["name"]}{defvals}>::bind(get_class_static(), D_METHOD("{method["bind_name"]}"{args}));\n'

				# TODO: virtual method bindings need
				# more work with GDExtension
				#elif method['is_virtual']:
				#	Hvirtual_method += f'\tMethod<&{class_name}::{method["name"]}>::bind_virtual("{method["bind_name"]}"{defvals});\n'

				else:
					Hmethod += f'\tMethod<&{class_name}::{method["name"]}>::bind(D_METHOD("{method["bind_name"]}"{args}){defvals});\n'

				if 'rpc_config' in method.keys():
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
				args_list = '\n'.join(f'\t\t,MakePropertyInfo<{type}>("{name}")' for type, name in method['varargs'])

				Hvaragr_method += f'\tMethod<&{class_name}::{method["name"]}>::bind_vararg("{method["bind_name"]}"' + ('\n' + args_list + '\n\t\t);\n' if args_list != '' else ');\n')

		prev_group, prev_subgroup = '', ''
		for prop in content['properties']:
			if prop['getter'] not in methods_list:
				Hmethod += f'\tMethod<&{class_name}::{prop["getter"]}>::bind(D_METHOD("{prop["getter"]}"));\n'
				property_set_get_defs += f'GENERATE_GETTER({class_name_full}::{prop["getter"]}, {class_name_full}::{prop["name"]});\n'
				gen_getters.append([prop["getter"], prop["name"]])

			if prop['setter'] not in methods_list:
				Hmethod += f'\tMethod<&{class_name}::{prop["setter"]}>::bind(D_METHOD("{prop["setter"]}", "value"));\n'
				property_set_get_defs += f'GENERATE_SETTER({class_name_full}::{prop["setter"]}, {class_name_full}::{prop["name"]});\n'
				gen_setters.append([prop["setter"], prop["name"]])

			group, subgroup = prop['group'], prop['subgroup']
			group_ = group_name(group)
			if group != '' and group != prev_group:
				Hprop += f'\tADD_GROUP("{group}", "{group_}");\n'
				prev_group = group

			subgroup_ = group_name(subgroup)
			if subgroup != '' and subgroup != prev_subgroup:
				Hprop += f'\tADD_SUBGROUP("{subgroup}", "{group_}{subgroup_}");\n'
				prev_subgroup = subgroup

			prop_name = group_ + subgroup_ + prop['name']
			hints = f', {prop["hint"]}, {prop["hint_string"]}' if prop['hint'] != None else ''
			Hprop += f'\t\tADD_PROPERTY(MakePropertyInfo<decltype({prop["name"]})>("{prop_name}"{hints}), "{prop["setter"]}", "{prop["getter"]}");\n'

		defs[class_name_full]['gen_setters'] = gen_setters
		defs[class_name_full]['gen_getters'] = gen_getters

		for signal_name, args in content['signals']:
			args_str = '\n'.join(f'\t\t,MakePropertyInfo<{arg_type}>("{arg_name}")' for arg_type, arg_name in args)
			Hsignal += f'\tADD_SIGNAL(MethodInfo("{signal_name}"' + ('\n' + args_str + '\n\t\t' if args_str != '' else '') + '));\n'

		for enum, consts in content['enum_constants'].items():
			outside_bind += f'VARIANT_ENUM_CAST({enum});\n'
			for const in consts:
				Henum += f'\tBIND_ENUM_CONSTANT({const});\n'

		for enum, consts in content['bitfields'].items():
			outside_bind += f'VARIANT_BITFIELD_CAST({enum});\n'
			for const in consts:
				Hbitfield += f'\tBIND_BITFIELD_FLAG({const});\n'

		for const in content['constants']:
			Hconst += f'\tBIND_CONSTANT({const});\n'

		header_rpc_config = 'void {}::_rpc_config() {{{}}}\n'.format(
				class_name_full, '\n' + header_rpc_config if header_rpc_config != '' else '')
		header_bind_methods = '\n\n'.join(i for i in [Hmethod, Hvirtual_method, Hstatic_method, Hvaragr_method, Hprop, Hsignal, Henum, Hbitfield, Hconst] if i != '')
		header_defs += [f'// {class_name_full} : {content["base"]}\n',
			'void {}::_bind_methods() {{{}}}\n'.format(
			class_name_full, '\n' + header_bind_methods if header_bind_methods != '' else ''),
			header_rpc_config] + \
			([property_set_get_defs] if property_set_get_defs != '' else []) + \
			([outside_bind] if outside_bind != '' else [])

	file_name = filename_to_gen_filename(file, src)
	if len(defs) != 0:
		header_include = '#include <cppscript_bindings.h>\n\n#include <{}>\n\nusing namespace godot;\n\n'.format(os.path.relpath(file, src).replace('\\', '/'))
		content = header_include + '\n'.join(header_defs)

	os.makedirs(os.path.dirname(file_name), exist_ok=True)
	with open(file_name, 'w') as fileopen:
		fileopen.write(content)


def write_register_header(defs, src, target):
	scripts_header = ''
	classes_register_levels = {name[12:] : [] for name in INIT_LEVELS}

	for file, classes in defs.items():
		if len(classes) == 0:
			continue

		scripts_header += '#include <{}>\n'.format(os.path.relpath(file, src).replace('\\', '/'))
		for class_name_full, content in classes.items():
			# Ensure parent classes are registered before children
			# by iterating throught pairs of (base_name, register_str)
			classes_register = classes_register_levels[content['init_level']]
			class_name, base = content['class_name'], content['base']
			dots = base.rfind(':')
			base = base if dots == -1 else base[dots+1:]
			for i in range(len(classes_register)):
				if class_name == classes_register[i][0]:
					classes_register.insert(i, (base, f"\tGDREGISTER_{content['type']}({class_name_full});\n"))
					break
			else:
				classes_register.append((base, f"\tGDREGISTER_{content['type']}({class_name_full});\n"))


	scripts_header += '\nusing namespace godot;\n\n'
	classes_register_str = ''
	for level_name, defs in classes_register_levels.items():
		registers = ''.join(i for _, i in defs)
		classes_register_str += '_FORCE_INLINE_ void _register_level_{}() {{{}}}\n\n'.format(
			level_name.lower(), '\n' + registers if registers != '' else '')

	scripts_header += classes_register_str

	with open(target, 'w') as file:
		file.write(scripts_header)


def write_property_header(new_defs, filepath):
	body = ''
	for _, file in new_defs.items():
		for class_name_full, content in file.items():
			gen_setgets = [f' \\\nGENERATE_GETTER_DECLARATION({g}, {n})' for g, n in content['gen_getters']] + [f' \\\nGENERATE_SETTER_DECLARATION({g}, {n})' for g, n in content['gen_setters']]
			body += f'#define GSETGET_{content["class_name"]}' + ''.join(gen_setgets) + '\n\n'
	
	with open(filepath, 'w') as file:
		file.write(body)

