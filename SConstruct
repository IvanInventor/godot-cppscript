import re
import clang.cindex
import json

SCRIPT_REGEX = re.compile('class\s+([\w_]+)(?:\s*:\s*(?:public\s+|private\s+|protected\s+)?([\w_]+))?[\s\n]*{[\s\n]*EXPORT_CLASS\(.*\);?|EXPORT_METHOD\((.*)\)[\s\n]+([\w<> ]+)\s+([\w_]+)\((.*)\)')

########## CLANG
def extract_methods_and_fields(translation_unit):

	godot_class = { 'name' : None,
			'properties' : [],
			'methods' : []
		}
	current_property = None

	def parse_cursor(cursor, depth = 0):
		#print('' * depth, f'{cursor.kind}')
		#print([i.spelling for i in cursor.get_tokens()])
		match cursor.kind:
			case clang.cindex.CursorKind.CLASS_DECL:
				#if godot_class['name'] != None:
				#	print("Multiple class definitions not allowed")
				#	exit(1)

				godot_class['name'] = cursor.spelling
				tokens = cursor.get_tokens()
				for token in tokens:
					if token.spelling == ':': # base class declaration after
						m = [next(tokens).spelling, next(tokens).spelling]
						match m:
							case ['public' | 'private' | 'protected' as type, base]:
								godot_class['base'] = base
							case [base]:
								godot_class['base'] = base

						break


			case clang.cindex.CursorKind.CXX_BASE_SPECIFIER:
                		godot_class['base'] = cursor.type.spelling

			case clang.cindex.CursorKind.CXX_METHOD:
				godot_class['methods'].append({	   'name' : cursor.spelling,
				      				   'return' : cursor.result_type.spelling,
				      				   'args' : [{  'name' : arg.type.spelling,
			    							'type' : arg.spelling} for arg in cursor.get_arguments()]})
			case clang.cindex.CursorKind.FIELD_DECL:
				if cursor.spelling != 'GCLASS':
					current_property = cursor.spelling
					godot_class['properties'].append({ 'name' : cursor.spelling,
									   'type' : cursor.type.spelling})

		for child in cursor.get_children():
			parse_cursor(child, depth + 1)


	parse_cursor(translation_unit.cursor)
	# Recursively traverse the child nodes
	
	return godot_class

def parse_cpp_file(filename):
	index = clang.cindex.Index.create()
	translation_unit = index.parse(filename, args=['-DGDCLASS'])

	if not translation_unit:
		print("Error: Failed to parse the translation unit!")
		return

	return extract_methods_and_fields(translation_unit)

def generate_register_header(target, source, env):
	defs = env['DEFS']
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
	
	with open('scripts.gen.h', 'w') as file:
		file.write(header)

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
	env['REGENERAGE'] = True
	print('Building scripts')
	defs[str(source[0])] = parse_cpp_file(str(source[0]))
	print("Parsed definitions: ", defs[str(source[0])])
	


def emitter(target, source, env):
	sources = [str(i) for i in source if str(i) != 'register_types.os']
	env.AddPreAction('register_types.os', generate_register_header)
	for src in sources:
		env.AddPreAction(str(src), build_scripts)
	return target, source

envcpp = SConscript('godot-cpp/SConstruct')
env = envcpp.Clone()
sources = Glob("*.cpp", exclude=['register_types.cpp'])
env['REGENERATE'] = False
env['SCRIPT_SOURCES'] = sources
env['GEN_HEADER'] = ['', '', '']
#TEST
defs = load_defs()
env['DEFS'] = defs
#print("------------------ TEST ---------------------")
#for name in sources:
#	cpp = str(name)
#	#print(f'For file {cpp}:')
#	#cpp_defs = extract_methods_and_fields(cpp, path=env['CPPPATH'])
#	cpp_defs = extract_methods_and_fields(cpp)
#	#print(json.dumps(defs, indent=2))
#	defs[cpp] = cpp_defs

#action = Action(build_scripts)
#builder = Builder(action=action, sources=sources)
#env.Append(BUILDERS={'Build_scripts' : builder})

#env.Replace(SHLIBEMITTER=emitter)
env.Append(SHLIBEMITTER=emitter)

library = env.SharedLibrary(
	'#bin/libscripts.so',
	source=sources + Glob('register_types.cpp'),
	)
env.Ignore(library, 'scripts.gen.h')
Default(library)
