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
	r = re.compile('class\s+([\w_]+)(?:\s*:\s*(?:public\s+|private\s+|protected\s+)?([\w_]+))?[\s\n]*{[\s\n]*EXPORT_CLASS\(.*\);?|EXPORT_METHOD\((.*)\)[\s\n]+([\w<> ]+)\s+([\w_]+)\((.*)\)')
	bind_methods = {}
	binds = {}

	for file in sources:
		with open('main.cpp', 'r') as file:
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
				class_inherit_name = matches[0] if matches != '' else 'Node'
				current_class = class_name
				bind_methods |= {class_name: []}

			elif matches[2] != '':
				#EXPORT_METHOD
				args = (get_arguments(matches[2]), matches[3], matches[4], matches[5])
				bind_methods[current_class] += [args]

	#Generate binding strings
	register_class_defs = ''
	register_class_str = ''

	for name, members in bind_methods.items():
		register_class_str += f'GDREGISTER_CLASS({name});'

		bind_methods_str = ''
		for args, func_ret, func_name, func_args in members:
			bind_methods_str += f'ClassDB::bind_method(D_METHOD(STR({func_name})), &{name}::{func_name});'

			#register_class_defs += f'{func_ret} {name}::{func_name}({func_args});'
		
		register_class_defs += f'void {name}::_bind_methods(){{{bind_methods_str}}};'
		#binds.append((f'REGISTER_CLASS_GEN_CODE_CLASS_{name}', bind_methods_str))
		print(f"For class {name}: '{bind_methods_str}'")

	

	
	binds['REGISTER_CLASSES_GEN_CODE'] = f'"{register_class_str}"'
	#register_class_defs = register_class_defs.replace('"', '\\"')
	binds['GPD_GEN_CLASS_DEFS'] = f'{register_class_defs}'
	print('GPD DEFS')
	print(register_class_defs)
	print()


	return binds

envcpp = SConscript('godot-cpp/SConstruct')

env = envcpp.Clone()

sources = Glob("*.cpp", exclude=['register_types.cpp'])
print([str(i) for i in sources])

env.Append(CXXFLAGS=['-fdiagnostics-color=always'])
env.Append(CPPDEFINES=make_bindings_macro([str(i) for i in sources]))

env.Substfile('register_types.cpp', {'@include_scripts@' : '\n'.join([f'#include "{str(i)}"' for i in sources])})
#print('\n'.join([f'#include "{str(i)}"' for i in sources]))
library = env.StaticLibrary(
        "#bin/main",
	source = sources + Glob('register_types.cpp'),
	)

Default(library)
