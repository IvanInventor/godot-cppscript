from clang.cindex import Index, TranslationUnit, CursorKind, TokenKind, AccessSpecifier
import os, sys, json, hashlib, shutil

if 'NOT_SCONS' not in os.environ.keys():
	from SCons.Script import Glob
	from SCons.Builder import Builder

	def create_cppscript_target(env, sources, cppscript_env, *args, **kwargs):
		if not 'CppScript' in env['BUILDERS'].keys():
			env.Append(BUILDERS={'CppScript' : CppScriptBuilder()})
		
		return env.CppScript(sources, cppscript_env, *args, **kwargs)

	class CppScriptBuilder():
		def __init__(self):
			self.builder = Builder(action=generate_header_scons, emitter=generate_header_emitter)

		def __call__(self, scons_env, source, call_args, cwd = os.getcwd(), *args, **kwargs):
			env, *other = call_args
			cppscript_src = os.path.join(os.path.dirname(__file__), 'src')
			# Convert scons variables to cppscript's env
			scons_env['cppscript_env'] = {
					'header_name' : env['header_name'],
					'header_dir' : resolve_path(str(env['header_dir']), cwd),
					'gen_dir' : resolve_path(str(env['gen_dir']), cwd),
					'compile_defs' : {f'{i[0]}={i[1]}' if type(i) is tuple else str(i) for i in env.get('compile_defs', [])},
					'include_paths' : {resolve_path(str(i), cwd) for i in [cppscript_src, env['header_dir']] + env.get('include_paths', [])},
					'auto_methods' : env['auto_methods']
				}

			# Append needed directories
			scons_env.Append(CPPPATH=[cppscript_src, resolve_path(env['header_dir'], cwd)])
			return self.builder(scons_env, source=source, *other, *args, **kwargs)


	def GlobRecursive(path, pattern, **kwargs):
		found = []
		for root, dirs, files in os.walk(path):
			if not os.path.basename(root).startswith('.'):
				found += Glob(root + '/' + pattern, **kwargs)
			else:
				dirs[:] = []

		return found


KEYWORDS = ['GPROPERTY', 'GMETHOD', 'GGROUP', 'GSUBGROUP', 'GBITFIELD', 'GSIGNAL', 'GRPC', 'GVARARG', 'GIGNORE', 'GBIND_METHODS_APPEND', 'GBIND_METHODS_PREPEND']
INIT_LEVELS = ['GINIT_LEVEL_CORE', 'GINIT_LEVEL_SERVERS', 'GINIT_LEVEL_SCENE', 'GINIT_LEVEL_EDITOR']

DONOTEDIT_MSG = "/*-- GENERATED FILE - DO NOT EDIT --*/\n\n"

CPPSCRIPT_BODY= DONOTEDIT_MSG + """#ifndef {0}
#define {0}
#include <cppscript_defs.h>
#include "properties.gen.h"
#endif // {0}
"""

RPC_CONFIG_BODY = """	{{
	Dictionary opts;
	opts["rpc_mode"] = MultiplayerAPI::{0};
	opts["transfer_mode"] = MultiplayerPeer::{1};
	opts["call_local"] = {2};
	opts["channel"] = {3};
	rpc_config("{4}", opts);
	}}
"""

# Helpers
class CppScriptException(Exception):
	pass


def replace_extension(filename, new_ext):
	idx = filename.rfind('.')
	if idx == -1:
		return filename + new_ext
	else:
		return filename[:idx] + new_ext


def resolve_path(path, cwd):
	return path if os.path.isabs(path) else os.path.abspath(os.path.join(cwd, path))


def filename_to_gen_filename(name, env):
	return os.path.join(env['gen_dir'], os.path.relpath(replace_extension(name, '.gen.cpp'), env['header_dir']))


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
	generated = [env.File(filename_to_gen_filename(str(i), env['cppscript_env'])) for i in source]

	# To avoid generated sources deletion and re-parsing
	env.Precious(generated)

	return generated, source


def generate_header_scons(target, source, env):
	if "CPPSCRIPT_DEBUG" in os.environ.keys():
		print(json.dumps(env['cppscript_env'], indent=2, default=lambda x: list(x) if type(x) is set else x))
	return generate_header(source, env['cppscript_env'], get_file_scons)


def generate_header_cmake(source, env):
	if "CPPSCRIPT_DEBUG" in os.environ.keys():
		print(json.dumps(env, indent=2, default=lambda x: list(x) if type(x) is set else x))
	return generate_header(source, env, get_file_cmake)


def generate_header(source, env, get_file):
	index = Index.create()
	prop_file_name = os.path.join(env['header_dir'], 'properties.gen.h') 

	# Move properties file if exists to avoid infinite cycle for auto-genereted getter/setters:
	# no method definition -> generate one -> parse  | 
	#     ^                                          V
	#     |   do NOT generate one   <-     method exists
	try:
		shutil.move(prop_file_name, prop_file_name + '.tmp')
	except:
		pass

	# Create include header if not exists
	path = os.path.join(env['header_dir'], env['header_name'])
	if not os.path.exists(path):
		with open(path, 'w') as file:
			file.write(CPPSCRIPT_BODY.format(env['header_name'].replace(' ', '_').replace('.', '_').upper()))

	try:
		defs_file_path = os.path.join(env['gen_dir'], 'defs.json')
		cached_defs_all = load_defs_json(defs_file_path)
		cached_defs = cached_defs_all.get('files', {})
		need_regen = False

		# Prepare parser args
		env['parser_args'] = [f'-I{i}' for i in env['include_paths']] + \
			[f'-D{i}' for i in env['compile_defs']] + \
			[f'-DGDCLASS']

		new_defs_files = {}
		for s in source:
			filename, file_content = get_file(s)
			new_hash = hashlib.md5(file_content.encode()).hexdigest()
			if not os.path.exists(filename_to_gen_filename(filename, env)) or filename not in cached_defs.keys() or new_hash != cached_defs[filename]['hash']:
				need_regen = True
				new_defs_files |= {filename : {'content' : parse_and_write_header(index, filename, file_content, env), 'hash' : new_hash}}
			else:
				new_defs_files |= {filename : cached_defs[filename]}

		new_defs_all = {'hash' : cached_defs_all.get('hash', None), 'files' : new_defs_files}

		if write_register_header(new_defs_all, env) or need_regen:
			write_property_header(new_defs_all, env)
			try:
				os.remove(prop_file_name + '.tmp')
			except:
				pass
		else:
			try:
				shutil.move(prop_file_name + '.tmp', prop_file_name)
			except:
				pass

		with open(defs_file_path, 'w') as file:
			json.dump(new_defs_all, file, indent=2, default=lambda x: x if not isinstance(x, set) else list(x))

	except CppScriptException as e:
		print(f'\n{e}\n', file=sys.stderr)
		return 1

	return 0

def parse_header(index, filename, filecontent, env):
	translation_unit = index.parse(filename, args=env['parser_args'] + ['-x', 'c++'], unsaved_files=[(filename, filecontent)], options=TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD)

	if not translation_unit:
		raise CppScriptException("{filename}: failed to create translation unit")

	classes_and_Gmacros = []
	keyword_macros = []
	def parse_class(parent, class_cursors):
		for cursor in parent.get_children():
			match cursor.kind:
				case CursorKind.CXX_METHOD:
					class_cursors.append(cursor)

				case CursorKind.FIELD_DECL:
					class_cursors.append(cursor)

				case CursorKind.ENUM_DECL:
					if cursor.access_specifier == AccessSpecifier.PUBLIC:
						class_cursors.append(cursor)


	def parse_cursor(parent):
		for cursor in parent.get_children():
			if cursor.location.file is None or cursor.location.file.name != filename:
				continue

			match cursor.kind:
				case CursorKind.CLASS_DECL:
					classes_and_Gmacros.append(cursor)

				case CursorKind.MACRO_INSTANTIATION:
					if cursor.spelling in KEYWORDS:
						keyword_macros.append(cursor)

					elif cursor.spelling in INIT_LEVELS:
						keyword_macros.append(cursor)

					elif cursor.spelling in ['GCLASS', 'GVIRTUAL_CLASS', 'GABSTRACT_CLASS', 'GINTERNAL_CLASS']:
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
			classes.append((cursor, macro))


	collapse_list(found_class, lambda x: x.kind == CursorKind.CLASS_DECL, add_class)

	parsed_classes = {}
	for cursor, gdclass_macro in classes:
		class_defs = {
			'class_name' : cursor.spelling,
			'base' : get_macro_args(filecontent, gdclass_macro)[1],
			'type' : gdclass_macro.spelling[1:],
			'init_level' : 'SCENE',
			'methods' : [],
			'properties' : [],
			'signals' : [],
			'enum_constants' : {},
			'constants' : [],
			'bitfields' : {},
			'bind_methods_append' : '',
			'bind_methods_prepend' : ''
			}
		child_cursors = []
		parse_class(cursor, child_cursors)
		# Exclude cursors added by GCLASS() macro
		child_cursors = [i for i in child_cursors if gdclass_macro.extent.start.offset != i.extent.start.offset]

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

					case 'GBIND_METHODS_APPEND':
						class_defs['bind_methods_append'] += get_macro_body(filecontent, macro)

					case 'GBIND_METHODS_PREPEND':
						class_defs['bind_methods_prepend'] += get_macro_body(filecontent, macro)


			return not is_ignored


		def apply_macros(item, macros):
			nonlocal group
			nonlocal subgroup
			properties = None
			match item.kind:
				case CursorKind.CXX_METHOD:
					is_virtual = is_virtual_method(item)
					properties = {}
					if process_macros(item, macros, properties, (is_virtual and item.spelling.startswith('_')) or not env['auto_methods'] or item.access_specifier != AccessSpecifier.PUBLIC):
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
			if macro.spelling not in ['GSIGNAL', 'GGROUP', 'GSUBGROUP', 'GBIND_METHODS_APPEND', 'GBIND_METHODS_PREPEND'] + INIT_LEVELS:
				raise CppScriptException('{}:{}:{}: error: macro without target member'
				.format(filename, macro.location.line, macro.location.column))
		process_macros(None, leftover, None)


		parsed_classes[cursor.type.spelling] = class_defs

	return parsed_classes


def parse_and_write_header(index, filename, filecontent, env):
	defs = parse_header(index, filename, filecontent, env)
	write_header(filename, defs, env)

	return defs


def write_header(file, defs, env):
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
					header_rpc_config += RPC_CONFIG_BODY.format(
						method['rpc_config']['rpc_mode'],
						method['rpc_config']['transfer_mode'],
						method['rpc_config']['call_local'],
						method['rpc_config']['channel'],
						method["name"]
						)
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
		header_bind_methods = content['bind_methods_append'] + header_bind_methods + content['bind_methods_prepend']

		header_defs += [f'// {class_name_full} : {content["base"]}\n',
			'void {}::_bind_methods() {{{}}}\n'.format(
			class_name_full, '\n' + header_bind_methods if header_bind_methods != '' else ''),
			header_rpc_config] + \
			([property_set_get_defs] if property_set_get_defs != '' else []) + \
			([outside_bind] if outside_bind != '' else [])

	gen_filename = filename_to_gen_filename(file, env)
	content = ''
	if len(defs) != 0:
		header_include = '#include <cppscript_bindings.h>\n\n#include "{}"\n\nusing namespace godot;\n\n'.format(os.path.relpath(file, os.path.dirname(gen_filename)).replace('\\', '/'))
		content = DONOTEDIT_MSG + header_include + '\n'.join(header_defs)

	os.makedirs(os.path.dirname(gen_filename), exist_ok=True)
	with open(gen_filename, 'w') as fileopen:
		fileopen.write(content)


def write_register_header(defs_all, env):
	target = os.path.join(env['header_dir'], 'scripts.gen.h')
	scripts_header = DONOTEDIT_MSG
	classes_register_levels = {name[12:] : [] for name in INIT_LEVELS}

	for file, filecontent in defs_all['files'].items():
		classes = filecontent['content']
		if len(classes) == 0:
			continue

		scripts_header += '#include "{}"\n'.format(os.path.relpath(file, os.path.dirname(target)).replace('\\', '/'))
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


	classes_register_str = ''
	if classes_register_levels['CORE'] != []:
		minimal_register_level = 'MODULE_INITIALIZATION_LEVEL_CORE'
	elif classes_register_levels['SERVERS'] != []:
		minimal_register_level = 'MODULE_INITIALIZATION_LEVEL_SERVERS'
	else:
		minimal_register_level = 'MODULE_INITIALIZATION_LEVEL_SCENE'

	scripts_header += '\nusing namespace godot;\n\n' + \
			f'static const ModuleInitializationLevel DEFAULT_INIT_LEVEL = {minimal_register_level};\n\n'
	for level_name, defs in classes_register_levels.items():
		registers = ''.join(i for _, i in defs)
		classes_register_str += '_FORCE_INLINE_ void _register_level_{}() {{{}}}\n\n'.format(
			level_name.lower(), '\n' + registers if registers != '' else '')

	scripts_header += classes_register_str

	new_hash = hashlib.md5(scripts_header.encode()).hexdigest()

	if new_hash != defs_all['hash']:
		with open(target, 'w') as file:
			file.write(scripts_header)
		defs_all['hash'] = new_hash

		return True

	return False


def write_property_header(new_defs, env):
	filepath = os.path.join(env['header_dir'], 'properties.gen.h')
	body = DONOTEDIT_MSG
	for filename, filecontent in new_defs['files'].items():
		classcontent = filecontent['content']
		for class_name_full, content in classcontent.items():
			gen_setgets = [f' \\\nGENERATE_GETTER_DECLARATION({g}, {n})' for g, n in content['gen_getters']] + [f' \\\nGENERATE_SETTER_DECLARATION({g}, {n})' for g, n in content['gen_setters']]
			body += f'#define GSETGET_{content["class_name"]}' + ''.join(gen_setgets) + '\n\n'

	with open(filepath, 'w') as file:
		file.write(body)

