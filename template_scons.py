#!/usr/bin/env python3
# THIS FILE IS AUTO-GENERATED
# See `https://github.com/IvanInventor/godot-cppscript/tree/next` for proper source

import sys, os

if __name__ == '__main__':
    # Ran as configure script

@PY_CONFIGURE_SCRIPT@

@PY_EMBED_SRC_FILES@

# Ran as module from SConstruct
from SCons.Script import Glob
from SCons.Builder import Builder

def create_cppscript_target(env, sources, cppscript_env, *args, **kwargs):
	if not 'CppScript' in env['BUILDERS'].keys():
		env.Append(BUILDERS={'CppScript' : CppScriptBuilder()})
	
	return env.CppScript(sources, cppscript_env, *args, **kwargs)

class CppScriptBuilder():
	def __call__(self, env, source, call_args, cwd = os.getcwd(), *args, **kwargs):
		cppscript_env, *other = call_args
		# Convert scons variables to cppscript's env
		cppscript_env = {
			'header_name' : cppscript_env['header_name'],
			'header_dir' : resolve_path(str(cppscript_env['header_dir']), cwd),
			'gen_dir' : resolve_path(str(cppscript_env['gen_dir']), cwd),
			'compile_defs' : {f'{i[0]}={i[1]}' if type(i) is tuple else str(i) for i in cppscript_env.get('compile_defs', [])},
			'include_paths' : {resolve_path(str(i), cwd) for i in [cppscript_env['header_dir']] + cppscript_env.get('include_paths', [])},
			'auto_methods' : cppscript_env['auto_methods'],
			'code_format' : code_format_godot_cpp()
				if os.getenv("CPPSCRIPT_NO_CONSTEXPR_CHECKS", False)
				else code_format_cppscript_constexr_checks()
			}
		env['cppscript_env'] = cppscript_env


		# Generate embedded headers once
		header_path = cppscript_env['header_dir']

		bindings = os.path.join(header_path, 'cppscript_bindings.h')
		defs = os.path.join(header_path, 'cppscript_defs.h')
		godotcpp = os.path.join(header_path, cppscript_env['header_name'])
		def generate_emitter(target, source, env):
			generated = [env.File(bindings), env.File(defs), env.File(godotcpp)]
			env.NoCache(generated)
			return generated, source

		def generate(target, source, env):
			with open(bindings, 'w') as file:
				file.write(CPPSCRIPT_BINDINGS_H)
			with open(defs, 'w') as file:
				file.write(CPPSCRIPT_DEFS_H)
			with open(godotcpp, 'w') as file:
				file.write(CPPSCRIPT_BODY_H.replace('@H_GUARD@', cppscript_env['header_name'].replace(' ', '_').replace('.', '_').upper()))
		
		def generate_header_emitter(target, source, env):
			generated = [env.File(filename_to_gen_filename(str(i), env['cppscript_env'])) for i in source]

			env.NoCache(generated)
			# To avoid generated sources deletion and re-parsing
			env.Precious(generated)

			return generated, source

		generator = Builder(action=generate, emitter=generate_emitter)(env)
		builder = Builder(action=generate_header_scons, emitter=generate_header_emitter) \
			(env, source=source, *other, *args, **kwargs)
		#env.Depends(builder, generator)

		return builder


def GlobRecursive(path, pattern, **kwargs):
	found = []
	for root, dirs, files in os.walk(path):
		if not os.path.basename(root).startswith('.'):
			found += Glob(root + '/' + pattern, **kwargs)
		else:
			dirs[:] = []

	return found


@CPPSCRIPT_PY_MODULE@

