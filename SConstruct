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
	r = re.compile('class\s+([\w_]+)(?:\s*:\s*(?:public\s+|private\s+|protected\s+)?([\w_]+))?[\s\n]*{[\s\n]*EXPORT_CLASS\(\s*[\w_]+\s*\);?|EXPORT_METHOD\((.*)\)[\s\n]+([\w<> ]+)\s+([\w_]+)\(.*\)')
	bind_methods = {}
	generated_binds = []

	for file in sources:
		with open('main.cpp', 'r') as file:
			text = file.read()

		#r = re.compile('(EXPORT_METHOD|EXPORT_CLASS)\((.*)\)')
		#print(r.findall(text))
		res = r.findall(text)

		print(res)
		current_class = None
		"""
		EXPORT_ARGS 0(class_name), 1(class_inherit)
		EXPORT_METHOD 2(args) 3(func_ret) 4(func_name)
		"""
		for matches in res:
				
			if matches[0] != '':
				#EXPORT_CLASS
				class_name = matches[0]
				class_inherit_name = matches[0] if matches != '' else 'Node'
				current_class = class_name
				bind_methods |= {class_name: []}
				generated_binds.append((f'GDP_CLASS_NAME_INH_{class_inherit_name}', class_inherit_name)) 

			elif matches[2] != '':
				#EXPORT_METHOD
				args = (get_arguments(matches[2]), matches[3], matches[4])
				bind_methods[current_class] += [args]

	#Generate binding strings
	generated_register_class_str = ''
	for name, members in bind_methods.items():
		generated_register_class_str += f'GDREGISTER_CLASS({name});'

		generated_bind_methods_str = ''
		for args, func_ret, func_name in members:
			generated_bind_methods_str += f'ClassDB::bind_method(D_METHOD("{func_name}"), &{name}::{func_name});'
		
		generated_binds.append((f'REGISTER_CLASS_GEN_CODE_CLASS_{name}', generated_bind_methods_str))

	print('Binded methods:')
	print(bind_methods)
	print('Strings:')
	print(generated_register_class_str)
	print()
	print(generated_binds)
	
	generated_binds.append(('REGISTER_CLASSES_GEN_CODE', f'"{generated_register_class_str}"'))


	return generated_binds

#env.Append(CPPPATH=["src/"])
sources = Glob("*.cpp", exclude=['register_types.cpp'])
print([str(i) for i in sources])
env = Environment()

env.Append(CXXFLAGS=['-fdiagnostics-color=always'])
env.Append(CPPDEFINES=make_bindings_macro([str(i) for i in sources]))


VariantDir('build', '.')

library = env.StaticLibrary(
        "#bin/main",
	['#build/' + str(i) for i in sources],
	)

Default(library)
