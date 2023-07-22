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
	register_class_template = """
#include "register_types.h"
#include <gdextension_interface.h>
#include <godot_cpp/core/class_db.hpp>
#include <godot_cpp/core/defs.hpp>
#include <godot_cpp/godot.hpp>
SCONS_GENERATED_CLASS_METHODS_DEFINITIONS
using namespace godot;
void initialize_example_module(ModuleInitializationLevel p_level) {
	if (p_level != MODULE_INITIALIZATION_LEVEL_SCENE) {
		return;
	}
	%s
}
void uninitialize_example_module(ModuleInitializationLevel p_level) {
	if (p_level != MODULE_INITIALIZATION_LEVEL_SCENE) {
		return;
	}
}
extern "C" GDExtensionBool GDE_EXPORT example_library_init(GDExtensionInterfaceGetProcAddress p_get_proc_address, GDExtensionClassLibraryPtr p_library, GDExtensionInitialization *r_initialization) {
	godot::GDExtensionBinding::InitObject init_obj(p_get_proc_address, p_library, r_initialization);

	init_obj.register_initializer(initialize_example_module);
	init_obj.register_terminator(uninitialize_example_module);
	init_obj.set_minimum_library_initialization_level(MODULE_INITIALIZATION_LEVEL_SCENE);

	return init_obj.init();
}
"""
	r = re.compile('EXPORT_CLASS\((.*)\);?|EXPORT_METHOD\((.*)\)[\s\n]+([\w<> ]+)\s+([\w_]+)\(.*\)')
	bind_methods = {}

	for file in sources:
		with open('main.cpp', 'r') as file:
			text = file.read()

		#r = re.compile('(EXPORT_METHOD|EXPORT_CLASS)\((.*)\)')
		#print(r.findall(text))
		res = r.findall(text)

		current_class = None
		"""
		EXPORT_ARGS 0("class_name, class_inherit")
		EXPORT_METHOD 1(args) 2(func_ret) 3(func_name)
		"""
		for matches in res:
				
			if matches[0] != '':
				#EXPORT_CLASS
				class_name, class_inherit_name = get_arguments(matches[0])
				current_class = class_name
				bind_methods |= {class_name: []}

			elif matches[3] != '':
				#EXPORT_METHOD
				args = (get_arguments(matches[1]), matches[2], matches[3])
				bind_methods[current_class] += [args]

	#Generate binding strings
	generated_register_class_str = ''
	generated_binds = []
	for name, members in bind_methods.items():
		generated_register_class_str += f'ClassDB::register_class<{name}>();\n'

		generated_bind_methods_str = ''
		for args, func_ret, func_name in members:
			generated_bind_methods_str += f'ClassDB::bind_method(D_METHOD("{func_name}"), &{name}::{func_name});'
		
		generated_binds.append((f'REGISTER_CLASS_GEN_CODE_CLASS_{name}', f'{generated_bind_methods_str}'))

	print('Binded methods:')
	print(bind_methods)
	print('Strings:')
	print(generated_register_class_str)
	print()
	print(generated_binds)
	
	return generated_binds

#env.Append(CPPPATH=["src/"])
sources = Glob("*.cpp")
print([str(i) for i in sources])
env = Environment()

env.Append(CPPDEFINES=make_bindings_macro([str(i) for i in sources]))
library = env.Program(
        "main",
        source=sources)
print("build")

Default(library)

