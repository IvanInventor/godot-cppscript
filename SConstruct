import re

def get_arguments(text):
	arguments = []
	stack = 0
	head = 0

	for idx in range(len(text)):
		char = text[idx]

		if char == '(':
			stack += 1
		elif char == ')':
			if stack > 0:
				stack -= 1
			else:
				raise ValueError("Unbalanced brackets in arguments.")

		if char == ',' and stack == 0:
			arguments.append(text[head:idx].strip())
			head = idx + 1

	if text[head:].strip():
		arguments.append(text[head:].strip())

	return arguments

def make_bindings_macro(sources):
	print("--- GENERATE BINDINGS ---")
	r = re.compile('class\s+([\w_]+)(?:\s*:\s*(?:public\s+|private\s+|protected\s+)?([\w_]+))?[\s\n]*{[\s\n]*EXPORT_CLASS\(.*\);?|EXPORT_METHOD\((.*)\)[\s\n]+([\w<> ]+)\s+([\w_]+)\((.*)\)')
	bind_methods = {}
	binds = {}

	for src in sources:
		with open(str(src), 'r') as file:
			text = file.read()

		#r = re.compile('(EXPORT_METHOD|EXPORT_CLASS)\((.*)\)')
		#print(r.findall(text))
		res = r.findall(text)

		current_class = None
		"""
		EXPORT_ARGS 0(class_name), 1(class_inherit)
		EXPORT_METHOD 2(args) 3(func_ret) 4(func_name) 5(func_args)
		"""
		for matches in res:
				
			if matches[0] != '':
				#EXPORT_CLASS
				class_name = matches[0]
				#class_inherit_name = matches[0] if matches != '' else 'Node'
				current_class = class_name
				bind_methods |= {class_name: []}

			elif matches[2] != '':
				#EXPORT_METHOD
				args = (get_arguments(matches[2]), matches[3], matches[4], matches[5])
				bind_methods[current_class] += [args]

	#Generate binding strings
	include_str = ''
	register_class_str = ''
	bind_members_str = ''

	for name, members in bind_methods.items():
		include_str += f'#include "{name}"\n'
		register_class_str += f'\tGDREGISTER_CLASS({name});\n'

		bind_methods_str = ''
		for args, func_ret, func_name, func_args in members:
			bind_methods_str += f'\tClassDB::bind_method(D_METHOD(STR({func_name})), &{name}::{func_name});\n'

			#bind_members_str += f'{func_ret} {name}::{func_name}({func_args});'
		
		bind_members_str += f'void {name}::_bind_methods() {{\n{bind_methods_str}\n}};\n'
		#binds.append((f'REGISTER_CLASS_GEN_CODE_CLASS_{name}', bind_methods_str))
		#print(f"For class {name}: '{bind_methods_str}'")

	register_class_str = f'void register_script_classes() {{\n{register_class_str}\n}}\n'

	gen_text = include_str + register_class_str + bind_members_str
	
	print("---GENERATED TEXT---")
	print(gen_text)
	print("--------------------")
	return gen_text

def build_scripts(target, source, env):

	print('Building scripts')
	print([str(i) for i in target])
	print([str(i) for i in source])
	return
	script_sources = [str(i) for i in source if str(i) != 'register_types.cpp']
	
	gen_text = make_bindings_macro(script_sources)
	#env.Append(CPPDEFINES=make_bindings_macro([str(i) for i in script_sources]))
	
	with open('scripts.gen.h', 'w') as file:
		file.write(gen_text)

def emitter(target, source, env):
	print("CUSTOM EMITTER")
	print(target, source)
	for src in source:
			env.AddPreAction(src, build_scripts)
	return target, source

envcpp = SConscript('godot-cpp/SConstruct')
envcpp.Dump()
env = envcpp.Clone()
sources = Glob("*.cpp")
env['SOURCES'] = sources
#action = Action(build_scripts)
#builder = Builder(action=action, sources=sources)
#env.Append(BUILDERS={'Build_scripts' : builder})


#env.Replace(SHLIBEMITTER=emitter)
env.Append(SHLIBEMITTER=emitter)

library = env.SharedLibrary(
	'#bin/libscripts.so',
	source=sources,
	)
env.Ignore(library, 'scripts.gen.h')
Default(library)
