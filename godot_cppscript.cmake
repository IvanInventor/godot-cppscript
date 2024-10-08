# THIS FILE IS AUTO-GENERATED
# See `https://github.com/IvanInventor/godot-cppscript/tree/next` for proper source
cmake_minimum_required(VERSION 3.12.4)

find_package(Python3 3.10 REQUIRED)

if(CMAKE_SCRIPT_MODE_FILE)
    # Ran as configure script

set(PY_CONFIGURE_SCRIPT "REGISTER_TYPES_CPP_IN = \"\"\"
#include <gdextension_interface.h>

#include <godot_cpp/core/class_db.hpp>
#include <godot_cpp/core/defs.hpp>
#include <godot_cpp/godot.hpp>

// Include custom headers here

#include \"register_types.h\"

using namespace godot;

void initialize_@LIBRARY_NAME@_module(ModuleInitializationLevel p_level) {
	switch (p_level) {
		case MODULE_INITIALIZATION_LEVEL_CORE:
			_register_level_core();
			break;
		case MODULE_INITIALIZATION_LEVEL_SERVERS:
			_register_level_servers();
			break;
		case MODULE_INITIALIZATION_LEVEL_SCENE:
			// Non-cppscript classes, static/global variables
			// initialization here

			_register_level_scene();
			break;
		case MODULE_INITIALIZATION_LEVEL_EDITOR:
			_register_level_editor();
			break;
		default:
			break;
	}
}

void uninitialize_@LIBRARY_NAME@_module(ModuleInitializationLevel p_level) {
	switch (p_level) {
		case MODULE_INITIALIZATION_LEVEL_CORE:
			_unregister_level_core();
			break;
		case MODULE_INITIALIZATION_LEVEL_SERVERS:
			_unregister_level_servers();
			break;
		case MODULE_INITIALIZATION_LEVEL_SCENE:
			// Non-cppscript classes, static/global variables
			// deinitialization here

			_unregister_level_scene();
			break;
		case MODULE_INITIALIZATION_LEVEL_EDITOR:
			_unregister_level_editor();
			break;
		default:
			break;
	}
}

extern \"C\" {
// GDExtension initialization
GDExtensionBool GDE_EXPORT @LIBRARY_NAME@_library_init(GDExtensionInterfaceGetProcAddress p_get_proc_address, GDExtensionClassLibraryPtr p_library, GDExtensionInitialization *r_initialization) {
	godot::GDExtensionBinding::InitObject init_obj(p_get_proc_address, p_library, r_initialization);

	init_obj.register_initializer(initialize_@LIBRARY_NAME@_module);
	init_obj.register_terminator(uninitialize_@LIBRARY_NAME@_module);
	init_obj.set_minimum_library_initialization_level(DEFAULT_INIT_LEVEL);

	return init_obj.init();
}
}


\"\"\"
REGISTER_TYPES_H_IN = \"\"\"
// Template file to use with godot-cppscript
#ifndef REGISTER_TYPES_H
#define REGISTER_TYPES_H

#include <godot_cpp/core/class_db.hpp>

#include \"scripts.gen.h\"

void initialize_@LIBRARY_NAME@_module(godot::ModuleInitializationLevel p_level);
void initialize_@LIBRARY_NAME@_module(godot::ModuleInitializationLevel p_level);

#endif // REGISTER_TYPES_H

\"\"\"
SCRIPTS_GDEXTENSION_IN = \"\"\"
[configuration]

entry_symbol = \"@LIBRARY_NAME@_library_init\"
compatibility_minimum = 4.1

[libraries]

macos.debug = \"res://../bin/lib@LIBRARY_NAME@.macos.template_debug.framework\"
macos.release = \"res://../bin/lib@LIBRARY_NAME@.macos.template_release.framework\"
windows.debug.x86_32 = \"res://../bin/lib@LIBRARY_NAME@.windows.template_debug.x86_32.dll\"
windows.release.x86_32 = \"res://../bin/lib@LIBRARY_NAME@.windows.template_release.x86_32.dll\"
windows.debug.x86_64 = \"res://../bin/lib@LIBRARY_NAME@.windows.template_debug.x86_64.dll\"
windows.release.x86_64 = \"res://../bin/lib@LIBRARY_NAME@.windows.template_release.x86_64.dll\"
linux.debug.x86_64 = \"res://../bin/lib@LIBRARY_NAME@.linux.template_debug.x86_64.so\"
linux.release.x86_64 = \"res://../bin/lib@LIBRARY_NAME@.linux.template_release.x86_64.so\"
linux.debug.arm64 = \"res://../bin/lib@LIBRARY_NAME@.linux.template_debug.arm64.so\"
linux.release.arm64 = \"res://../bin/lib@LIBRARY_NAME@.linux.template_release.arm64.so\"
linux.debug.rv64 = \"res://../bin/lib@LIBRARY_NAME@.linux.template_debug.rv64.so\"
linux.release.rv64 = \"res://../bin/lib@LIBRARY_NAME@.linux.template_release.rv64.so\"
android.debug.x86_64 = \"res://../bin/lib@LIBRARY_NAME@.android.template_debug.x86_64.so\"
android.release.x86_64 = \"res://../bin/lib@LIBRARY_NAME@.android.template_release.x86_64.so\"
android.debug.arm64 = \"res://../bin/lib@LIBRARY_NAME@.android.template_debug.arm64.so\"
android.release.arm64 = \"res://../bin/lib@LIBRARY_NAME@.android.template_release.arm64.so\"
web.debug.wasm32 = \"res://../bin/lib@LIBRARY_NAME@.web.template_debug.wasm32.wasm\"

\"\"\"


import os, sys
argv = sys.argv[1:]

try:
    library_name = argv[0].replace('-', '_')
    cpp_path = argv[1]
    h_path = argv[2]
    gdext_path = argv[3]
except:
    ABOUT = \\
'''
ERROR: Not enough arguments.
Needed arguments (<argument> - example):

<library_name>              (`my_library_name`)
<cpp_file_path>             (`src/register_types.cpp`)
<header_file_path>          (`include/register_types.h`)
<gdextension_file_path>     (`project/my_library.gdextension`)
'''
    print(ABOUT, file=sys.stderr)
    exit(1)

prompt = f'''These files will be affected:
    {'(New)     ' if not os.path.exists(gdext_path) else '(Override)'} {gdext_path}
    {'(New)     ' if not os.path.exists(cpp_path) else '(Override)'} {cpp_path}
    {'(New)     ' if not os.path.exists(h_path) else '(Override)'} {h_path}
'''
print(prompt)
while True:
    inp = input('Are you sure? (Y/N) ')
    if inp == '':
        continue
    if inp not in 'yY':
        print('No changes, exiting...')
        exit(1)
    break

print(f\"Configuring '{gdext_path}' ...\")
open(gdext_path, 'w').write(
    SCRIPTS_GDEXTENSION_IN.replace('@LIBRARY_NAME@', library_name))

print(f\"Configuring '{cpp_path}' ...\")
open(cpp_path, 'w').write(
    REGISTER_TYPES_CPP_IN.replace('@LIBRARY_NAME@', library_name))

print(f\"Configuring '{h_path}' ...\")
open(h_path, 'w').write(
    REGISTER_TYPES_H_IN.replace('@LIBRARY_NAME@', library_name))

print(\"Files configured.\")
exit(0)
"
)


	# Pass args to python config script
	math(EXPR ARGC "${CMAKE_ARGC} - 1")
	foreach(i RANGE 3 ${ARGC})
		list(APPEND ARGS "${CMAKE_ARGV${i}}")
	endforeach()

	set(SCRIPT_PATH "${CMAKE_CURRENT_SOURCE_DIR}/.configure_script.py.tmp")
	file(WRITE ${SCRIPT_PATH} "${PY_CONFIGURE_SCRIPT}")
   execute_process(
      COMMAND
         "${Python3_EXECUTABLE}"
			"${SCRIPT_PATH}"
			${ARGS}
      WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
   )
	file(REMOVE ${SCRIPT_PATH})

else()

set(CPPSCRIPT_BODY_H "#ifndef @H_GUARD@
#define @H_GUARD@
#include \"cppscript_defs.h\"
#include \"properties.gen.h\"
#endif // @H_GUARD@
"
)
set(CPPSCRIPT_DEFS_H "#ifndef CPPSCRIPT_HEADER
#define CPPSCRIPT_HEADER

#define GCLASS(CLASS_NAME, CLASS_NAME_INH) 								\\
	GDCLASS(CLASS_NAME , CLASS_NAME_INH)								\\
protected:												\\
static void _bind_methods();										\\
protected:												\\
void _rpc_config();											\\
public:													\\
GSETGET_ ## CLASS_NAME											\\
private:

#define GVIRTUAL_CLASS(CLASS_NAME, CLASS_NAME_INH) GCLASS(CLASS_NAME, CLASS_NAME_INH)
#define GABSTRACT_CLASS(CLASS_NAME, CLASS_NAME_INH) GCLASS(CLASS_NAME, CLASS_NAME_INH)
#define GINTERNAL_CLASS(CLASS_NAME, CLASS_NAME_INH) GCLASS(CLASS_NAME, CLASS_NAME_INH)

#define GENERATE_GETTER_DECLARATION(function, prop_type)	\\
prop_type function();

#define GENERATE_SETTER_DECLARATION(function, prop_type)	\\
void function(prop_type);

#define GENERATE_GETTER(function, property, prop_type)	\\
prop_type function() {			\\
	return property;			\\
}

#define GENERATE_SETTER(function, property, prop_type)	\\
void function(prop_type value) {	\\
	this->property = value;			\\
}

#define GPROPERTY(...)
#define GMETHOD(...)
#define GGROUP(...)
#define GSUBGROUP(...)
#define GCONSTANT(...)
#define GBITFIELD(...)
#define GSIGNAL(...)
#define GRPC(...)
#define GVARARG(...)
#define GIGNORE(...)
#define GINIT_LEVEL_CORE(...)
#define GINIT_LEVEL_SERVERS(...)
#define GINIT_LEVEL_SCENE(...)
#define GINIT_LEVEL_EDITOR(...)
#define GBIND_METHODS_APPEND(...)
#define GBIND_METHODS_PREPEND(...)
#define GRESOURCE_LOADER(...)
#define GRESOURCE_SAVER(...)
#define GEDITOR_PLUGIN(...)
#define GSINGLETON(...);

#define GSTATIC_MEMBER(s_type, s_name, ...)												\\
friend impl::StaticAccess;																		\\
alignas(s_type) static char s_name ## _impl [sizeof(s_type)];						\\
static inline s_type& s_name = *reinterpret_cast<s_type*>(&s_name ## _impl);

namespace impl {
struct StaticAccess;
};

/* Similar to Godot engine's SNAME macro idea or GDScript's `&\"string_name\"` syntax,
 * it creates static instance of StringName and returns reference to it.
 * It guarantees that `StringName` exists before calling this lambda,
 * but not that `StringName`s with same string literal are the same object.
 */
#define SNAME(str_literal) ([]() -> const ::godot::StringName& {static const ::godot::StringName str(str_literal); return str;}())

#endif // CPPSCRIPT_HEADER
"
)
set(CPPSCRIPT_BINDINGS_H "#ifndef CPPSCRIPT_BINDINGS_H
#define CPPSCRIPT_BINDINGS_H

#include <type_traits>
#include <godot_cpp/core/class_db.hpp>
#include <godot_cpp/classes/ref.hpp>
#include <godot_cpp/classes/resource.hpp>
#include <godot_cpp/core/type_info.hpp>
#include <gdextension_interface.h>


namespace impl {

template <typename T, typename = void>
struct is_defined : std::false_type {};

template <typename T>
struct is_defined<T, std::void_t<decltype(T::VARIANT_TYPE)>> : std::true_type {};

template<class T>
struct is_supported_type {
	static constexpr bool value = is_defined<godot::GetTypeInfo<T>>::value;
};

// MSVC needs this for no reason
template<class T>
struct is_supported_type<godot::BitField<T>> {
	static constexpr bool value = true;
};

template<>
struct is_supported_type<godot::Variant**> {
	static constexpr bool value = true;
};

template<>
struct is_supported_type<const godot::Variant**> {
	static constexpr bool value = true;
};

template<>
struct is_supported_type<GDExtensionCallError&> {
	static constexpr bool value = true;
};
//

template<class T>
struct assert_is_supported_type {
	static constexpr bool value = is_supported_type<T>::value;
	static_assert(is_supported_type<T>::value, \"Type not supported. If it's your custom class, either it had complilation errors, or maybe you forgot to register it with GCLASS()\");
};

template<class T>
struct assert_is_ret_supported {
	static constexpr bool value = assert_is_supported_type<T>::value;
};
template<>
struct assert_is_ret_supported<void> {
	static constexpr bool value = true;
};

template <typename>
struct MemberSignature;

template <typename Class, typename Ret, typename... Args>
struct MemberSignature<Ret (Class::*)(Args...) const> {
	static constexpr bool value = assert_is_ret_supported<Ret>::value && (assert_is_supported_type<Args>::value && ...);
};

template <typename Class, typename Ret, typename... Args>
struct MemberSignature<Ret (Class::*)(Args...)> {
	static constexpr bool value = assert_is_ret_supported<Ret>::value && (assert_is_supported_type<Args>::value && ...);
};

template <typename Ret, typename... Args>
struct FunctionSignature;

template <typename Ret, typename... Args>
struct FunctionSignature<Ret (*)(Args...)> {
	static constexpr bool value = assert_is_ret_supported<Ret>::value && (assert_is_supported_type<Args>::value && ...);
};


template <typename Class, typename Ret, typename... Args>
static constexpr auto is_method_signature_supported(Ret (Class::*func)(Args...) const) {
    return MemberSignature<decltype(func)>();
}

template <typename Class, typename Ret, typename... Args>
static constexpr auto is_method_signature_supported(Ret (Class::*func)(Args...)) {
    return MemberSignature<decltype(func)>();
}

template <typename Ret, typename... Args>
static constexpr auto is_function_signature_supported(Ret (*func)(Args...)) {
	return FunctionSignature<decltype(func)>();
}

template<class T>
struct IsResourceProperty;

template<class T>
struct IsResourceProperty {
	static constexpr bool value = godot::TypeInherits<godot::Resource, T>::value;
	using type = T;
};

template<class T>
struct IsResourceProperty<godot::Ref<T>> {
	static constexpr bool value = godot::TypeInherits<godot::Resource, T>::value;
	using type = T;
};


template<bool b>
struct BindCheck;

template<>
struct BindCheck<true> {
	template<class... Args>
	static _FORCE_INLINE_ void bind(Args... args) {
		godot::ClassDB::bind_method(args...);
	};

	template<class... Args>
	static _FORCE_INLINE_ void bind_static(Args... args) {
		godot::ClassDB::bind_static_method(args...);
	};

	template <auto Ptr, typename Class, typename Ret, typename... Args, typename Name_t>
	static _FORCE_INLINE_ void bind_virtual(Ret (Class::*func)(Args...), Name_t name) {
		auto _call_method = [](GDExtensionObjectPtr p_instance, const GDExtensionConstTypePtr *p_args, GDExtensionTypePtr p_ret) -> void {
			godot::call_with_ptr_args(reinterpret_cast<Class *>(p_instance), Ptr, p_args, p_ret);
		};
		godot::ClassDB::bind_virtual_method(Class::get_class_static(), name, _call_method); 
	};

	template<class T, class ...Args>
	static _FORCE_INLINE_ godot::PropertyInfo MakePropertyInfo(Args&&... args) {
		return godot::PropertyInfo(godot::GetTypeInfo<T>::VARIANT_TYPE, std::forward<Args>(args)...);
	}

};

template<>
struct BindCheck<false> {
	template<class... Args>
	static _FORCE_INLINE_ void bind(Args... args) {};

	template<class... Args>
	static _FORCE_INLINE_ void bind_static(Args... args) {};

	template <auto Ptr, typename Class, typename Ret, typename... Args, typename Name_t>
	static _FORCE_INLINE_ void bind_virtual(Ret (Class::*func)(Args...), Name_t) {};


	template<class T, class ...Args>
	static _FORCE_INLINE_ godot::PropertyInfo MakePropertyInfo(Args&&... args) {
		return godot::PropertyInfo();
	}
};

template<class T>
_FORCE_INLINE_ void destroy_object(T& obj) {
	obj.~T();
}

}; // namespace impl

template<class T, class ...Args>
_FORCE_INLINE_ godot::PropertyInfo MakePropertyInfo(Args&&... args) {
	static_assert(impl::assert_is_supported_type<T>::value, \"Property of this type is not supported\");
	
	using IsResource = impl::IsResourceProperty<T>;
	if constexpr(sizeof...(Args) == 1 && IsResource::value) {
		return impl::BindCheck<impl::assert_is_supported_type<T>::value>::template MakePropertyInfo<T>(std::forward<Args>(args)..., godot::PROPERTY_HINT_RESOURCE_TYPE, IsResource::type::get_class_static());
	} else {
		return impl::BindCheck<impl::assert_is_supported_type<T>::value>::template MakePropertyInfo<T>(std::forward<Args>(args)...);
	}
}

template<auto Ptr>
struct Method {
	static constexpr bool is_supported = decltype(impl::is_method_signature_supported(Ptr))::value;

	template<class DMETHOD_t, class ...Args>
	static _FORCE_INLINE_ void bind(DMETHOD_t dmethod, Args... args) {
		impl::BindCheck<is_supported>::bind(dmethod, Ptr, args...);
	}

	template<class Name_t>
	static _FORCE_INLINE_ void bind_virtual(Name_t name) {
		impl::BindCheck<is_supported>::template bind_virtual<Ptr>(Ptr, name);
	}

	template<class Name_t, class ...Args>
	static _FORCE_INLINE_ void bind_vararg(Name_t name, Args&&... args) {
		godot::MethodInfo mi;
		mi.name = name;
		(mi.arguments.push_back(std::forward<Args>(args)), ...);

		godot::ClassDB::bind_vararg_method(godot::METHOD_FLAGS_DEFAULT, name, Ptr, mi);
	}


};
template<auto Ptr>
struct StaticMethod {
	static constexpr bool is_supported = decltype(impl::is_function_signature_supported(Ptr))::value;

	template<class DMETHOD_t, class ...Args>
	static _FORCE_INLINE_ void bind(const godot::StringName& name, DMETHOD_t dmethod, Args... args) {
		impl::BindCheck<true>::bind_static(name, dmethod, Ptr, args...);	
	}
};

#endif //CPPSCRIPT_BINDINGS_H
"
)
set(CPPSCRIPT_EMBED_PY_SCRIPT "from clang.cindex import Index, TranslationUnit, CursorKind, TokenKind, AccessSpecifier
import os, sys, json, hashlib, shutil

### CODE FORMAT ###
# (...) explains arguments for .format(...) call

class code_format_godot_cpp:
	DONOTEDIT_MSG = \"/*-- GENERATED FILE - DO NOT EDIT --*/\\n\\n\"

	# (header_guard)
	CPPSCRIPT_BODY = DONOTEDIT_MSG + \\
\"\"\"#ifndef {0}
#define {0}
#include <cppscript_defs.h>
#include \"properties.gen.h\"
#endif // {0}
\"\"\"

	# (rpc_mode, transfer_mode, call_local, method_name)
	RPC_CONFIG_BODY = \\
\"\"\"	{{
	Dictionary opts;
	opts[\"rpc_mode\"] = MultiplayerAPI::{0};
	opts[\"transfer_mode\"] = MultiplayerPeer::{1};
	opts[\"call_local\"] = {2};
	opts[\"channel\"] = {3};
	rpc_config(\"{4}\", opts);
	}}
\"\"\"
	
	# (code)
	STATIC_ACCESS_CLASS_BODY = \\
\"\"\"namespace impl {{
struct StaticAccess {{
{}}};
}};

\"\"\"

	# (type, name, args)
	PROPERTY_INFO = 'PropertyInfo(GetTypeInfo<{0}>::VARIANT_TYPE, \"{1}\"{2})'

	# (value)
	ARGNAMES_SEPARATOR = ', \"{0}\"'

	# (value)
	DEFAULT_VALUES_SEPARATOR = ', DEFVAL({0})'

	# (class_name, method_name, method_bind_name, args, default_values)
	METHOD_REGISTER = '\\tClassDB::bind_method(D_METHOD(\"{2}\"{3}), &{0}::{1}{4});\\n'

	# (class_name, method_name, method_bind_name, args, default_values)
	STATIC_METHOD_REGISTER = '\\tClassDB::bind_static_method(get_class_static(), D_METHOD(\"{2}\"{3}),	&{0}::{1}{4});\\n'

	@classmethod
	def expand_property_info_list(cls, args):
		return '\\n'.join(f'\\t\\tmi.arguments.push_back({cls.PROPERTY_INFO.format(type, name, \"\")});' for type, name in args)

	# (class_name, method_name, method_bind_name, property_list)
	VARARG_REGISTER = \\
\"\"\"	{{
		MethodInfo mi;
{3}
		mi.name = \"{2}\";
		ClassDB::bind_vararg_method(METHOD_FLAGS_DEFAULT, \"{2}\", &{0}::{1}, mi);
	}}
\"\"\"

	# (class_name_full, method_name, property_name, property_type)
	GENERATE_GETTER = 'GENERATE_GETTER({0}::{1}, {0}::{2}, {3});\\n'

	# (method_name, property_type)
	GENERATE_GETTER_DECLARATION = 'GENERATE_GETTER_DECLARATION({0}, {1})'

	# (class_name_full, method_name, property_name, property_type)
	GENERATE_SETTER = 'GENERATE_SETTER({0}::{1}, {0}::{2}, {3});\\n'
 	
	# (method_name, property_type)
	GENERATE_SETTER_DECLARATION = 'GENERATE_SETTER_DECLARATION({0}, {1})'

	# (group_name, groug_name_expanded)
	ADD_GROUP = '\\tADD_GROUP(\"{0}\", \"{1}\");\\n'
 
	# (subgroup_name, subgroug_name_expanded)
	ADD_SUBGROUP = '\\tADD_SUBGROUP(\"{0}\", \"{1}\");\\n'
 
 	# (hint, other_args)
	PROPERTY_HINTS = ', {0}, {1}'

 	# (property_info, setter, getter)
	ADD_PROPERTY = '\\t\\tADD_PROPERTY({0}, \"{1}\", \"{2}\");\\n'

	# (signal_name, property_info_list)
	ADD_SIGNAL = '\\tADD_SIGNAL(MethodInfo(\"{0}\"{1}));\\n'

	# (name)
	VARIANT_ENUM_CAST = 'VARIANT_ENUM_CAST({0});\\n'
	
	# (name)
	BIND_ENUM_CONSTANT = '\\tBIND_ENUM_CONSTANT({0});\\n'

 	# (name)
	VARIANT_BITFIELD_CAST = 'VARIANT_BITFIELD_CAST({0});\\n'

	# (name)
	BIND_BITFIELD_FLAG = '\\tBIND_BITFIELD_FLAG({0});\\n'

	# (name)
	BIND_CONSTANT = '\\tBIND_CONSTANT({0});\\n'

	#(CLASS_TYPE, class_name)
	REGISTER_CLASS = '\\tGDREGISTER_{0}({1});\\n'


class code_format_cppscript_constexr_checks(code_format_godot_cpp):
	# (type, name, args)
	PROPERTY_INFO = 'MakePropertyInfo<{0}>(\"{1}\"{2})'

	@classmethod
	def expand_property_info_list(cls, args):
		return '\\n'.join(f'\\t\\t,' + cls.PROPERTY_INFO.format(type, name, '') for type, name in args)

	# (class_name, method_name, method_bind_name, args, default_values)
	METHOD_REGISTER = '\\tMethod<&{0}::{1}>::bind(D_METHOD(\"{2}\"{3}){4});\\n'

	# (class_name, method_name, method_bind_name, args, default_values)
	STATIC_METHOD_REGISTER = '\\tStaticMethod<&{0}::{1}>::bind(get_class_static(), D_METHOD(\"{2}\"{3}){4});\\n'

	# (class_name, method_name, method_bind_name, property_list)
	VARARG_REGISTER = '\\tMethod<&{0}::{1}>::bind_vararg(\"{2}\"{3});\\n'


###################

CLASS_KEYWORDS = [
	'GCLASS',
	'GVIRTUAL_CLASS',
	'GABSTRACT_CLASS',
	'GINTERNAL_CLASS'
]
INIT_LEVELS = [
	'GINIT_LEVEL_CORE',
	'GINIT_LEVEL_SERVERS',
	'GINIT_LEVEL_SCENE',
	'GINIT_LEVEL_EDITOR'
]
KEYWORDS = [
	'GPROPERTY',
	'GMETHOD',
	'GBITFIELD',
	'GRPC',
	'GVARARG',
	'GIGNORE'
]
TARGETLESS_KEYWORDS = [
	'GGROUP',
	'GSUBGROUP',
	'GSIGNAL',
	'GBIND_METHODS_APPEND',
	'GBIND_METHODS_PREPEND',
	'GRESOURCE_LOADER',
	'GRESOURCE_SAVER',
	'GEDITOR_PLUGIN',
	'GSINGLETON',
	'GSTATIC_MEMBER'
] + INIT_LEVELS

ALL_KEYWORDS = KEYWORDS + TARGETLESS_KEYWORDS


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
			case '\\\\':
				escaped = True
				continue

			case '\"':
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
	return '' if name == '' else (name.lower().replace(\" \", \"\") + \"_\")

 
def get_file_scons(scons_file):
	return str(scons_file), scons_file.get_text_contents()


def get_file_cmake(filename):
	with open(filename, 'r') as file:
		filecontent = file.read()

	return filename, filecontent


def is_virtual_method(cursor):
	for token in cursor.get_tokens():
		if (token.kind, token.spelling) in [(TokenKind.IDENTIFIER, \"override\"), (TokenKind.KEYWORD, \"virtual\")]:
			return True

	return False


def cursor_get_field_type(cursor):
	spelling = cursor.spelling
	tokens = list(cursor.get_tokens())
	for i in range(len(tokens)):
		if tokens[i].kind == TokenKind.IDENTIFIER and tokens[i].spelling == spelling:
			return ''.join(t.spelling for t in tokens[:i])

	raise CppScriptException('{}:{}:{}: error: cannot extract type from property \"{}\"'
	.format(cursor.location.file.name, cursor.location.line, cursor.location.column, cursor.spelling))


# Builder
def generate_header_scons(target, source, env):
	if \"CPPSCRIPT_DEBUG\" in os.environ.keys():
		print(json.dumps(env['cppscript_env'], indent=2, default=lambda x: list(x) if type(x) is set else x))
	return generate_header(source, env['cppscript_env'], get_file_scons)


def generate_header_cmake(source, env):
	if \"CPPSCRIPT_DEBUG\" in os.environ.keys():
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

	try:
		defs_file_path = os.path.join(env['gen_dir'], 'defs.json')
		cached_defs_all = load_defs_json(defs_file_path)
		cached_defs = cached_defs_all.get('files', {})
		need_regen = False

		# Prepare parser args
		env['parser_args'] = [f'-I{i}' for i in env['include_paths']] + \\
			[f'-D{i}' for i in env['compile_defs']] + \\
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
		print(f'\\n{e}\\n', file=sys.stderr)
		return 1

	return 0

def parse_header(index, filename, filecontent, env):
	translation_unit = index.parse(filename, args=env['parser_args'] + ['-x', 'c++'], unsaved_files=[(filename, filecontent)], options=TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD)

	if not translation_unit:
		raise CppScriptException(\"{filename}: failed to create translation unit\")

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
					if cursor.spelling in ALL_KEYWORDS:
						keyword_macros.append(cursor)

					elif cursor.spelling in CLASS_KEYWORDS:
						classes_and_Gmacros.append(cursor)

				case _:
					parse_cursor(cursor)

	parse_cursor(translation_unit.cursor)
	found_class = sorted(classes_and_Gmacros, key=lambda x: x.extent.start.offset, reverse=True)
	classes = []
	def add_class(cursor, macros):
		if len(macros) > 1:
			wrong_macro = macros[-2]
			raise CppScriptException('{}:{}:{}: error: repeated class macro for \"{}\" class defined at {}:{}'
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
			'static_members' : [],
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
							'args' : ', '.join(args[3:]) if len(args) > 3 else '\"\"'
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
										raise CppScriptException('{}:{}:{}: error: \"{}\" is not a keyword or channel id'
										.format(filename, macro.location.line, macro.location.column, arg))

									if channel != None:
										raise CppScriptException('{}:{}:{}: error: duplicate channel id usage'
										.format(filename, macro.location.line, macro.location.column))

									channel = arg

						rpc_config = {
							'rpc_mode' : 'RPC_MODE_' + rpc_mode if rpc_mode != None else 'RPC_MODE_AUTHORITY',
							'transfer_mode' : 'TRANSFER_MODE_' + transfer_mode if transfer_mode != None else 'TRANSFER_MODE_UNRELIABLE',
							'call_local' : call_local if call_local != None else 'false',
							'channel' : channel if channel != None else '0'
							}

						properties['rpc_config'] = rpc_config 

					case 'GVARARG':
						if item.kind != CursorKind.CXX_METHOD:
							raise CppScriptException('{}:{}:{}: error: incorrect {} macro usage on definition at {}:{}: must be member function'
							.format(filename, macro.location.line, macro.location.column, macro.spelling, item.location.line, item.location.column))

						properties['varargs'] = get_pair_arglist(get_macro_args(filecontent, macro), 'Variant')

					case 'GIGNORE':
						is_ignored = True

					case 'GBIND_METHODS_APPEND':
						class_defs['bind_methods_append'] += '\\n' + get_macro_body(filecontent, macro) + '\\n'

					case 'GBIND_METHODS_PREPEND':
						class_defs['bind_methods_prepend'] += '\\n' + get_macro_body(filecontent, macro) + '\\n'

					case 'GRESOURCE_LOADER':
						class_defs['is_resource_loader'] = True

					case 'GRESOURCE_SAVER':
						class_defs['is_resource_saver'] = True

					case 'GEDITOR_PLUGIN':
						class_defs['init_level'] = 'EDITOR'
						class_defs['is_editor_plugin'] = True

					case 'GSINGLETON':
						class_defs['is_singleton'] = True

					case 'GSTATIC_MEMBER':
						type, name, *init = get_macro_args(filecontent, macro)
						class_defs['static_members'].append((type, name, ', '.join(init)))


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
						properties |= {
							'name' : item.spelling,
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
						properties |= {
							'name': item.spelling,
							'type' : cursor_get_field_type(item),
							'group' : group,
							'subgroup' : subgroup,
							'is_static' : item.is_static_method()
							}

						class_defs['properties'].append(properties)



		leftover = collapse_list(class_macros, lambda x: x.kind != CursorKind.MACRO_INSTANTIATION, apply_macros)
		for macro in leftover:
			if macro.spelling not in TARGETLESS_KEYWORDS:
				raise CppScriptException('{}:{}:{}: error: macro \"{}\" without target member'
				.format(filename, macro.location.line, macro.location.column, macro.spelling))
		process_macros(None, leftover, None)


		parsed_classes[cursor.type.spelling] = class_defs

	return parsed_classes


def parse_and_write_header(index, filename, filecontent, env):
	defs = parse_header(index, filename, filecontent, env)
	write_header(filename, defs, env)

	return defs


def write_header(file, defs, env):
	CODE_FORMAT = env['code_format']
	header_defs = []
	global_variables = []
	for class_name_full, content in defs.items():
		class_name = content['class_name']
		Hmethod, Hstatic_method, Hvirtual_method, Hvaragr_method, Hprop, Hsignal, Henum, Hbitfield, Hconst = '', '', '', '', '', '', '', '', ''
		outside_bind, header_rpc_config, property_set_get_defs = '', '', ''
		gen_setters, gen_getters = [], []
		methods_list = [method['bind_name'] for method in content['methods']]
		has_rpc_config = False

		for method in content['methods']:
			if 'varargs' not in method.keys():
				args = ''.join(
						CODE_FORMAT.ARGNAMES_SEPARATOR.format(argname)
							if argname != '' else '' for argtype, argname, _ in method['args'])

				defvals = ''.join(
						CODE_FORMAT.DEFAULT_VALUES_SEPARATOR.format(defval)
							for _, _, defval in method['args'] if defval != '')

				if method['is_static']:
					Hstatic_method += CODE_FORMAT.STATIC_METHOD_REGISTER.format(
						class_name,
						method[\"name\"],
						method[\"bind_name\"],
						args,
						defvals
					)

				# TODO: virtual method bindings need
				# more work with GDExtension
				#elif method['is_virtual']:
				#	Hvirtual_method += f'\\tMethod<&{class_name}::{method[\"name\"]}>::bind_virtual(\"{method[\"bind_name\"]}\"{defvals});\\n'

				else:
					Hmethod += CODE_FORMAT.METHOD_REGISTER.format(
						class_name,
						method[\"name\"],
						method[\"bind_name\"],
						args,
						defvals
					)

				if 'rpc_config' in method.keys():
					has_rpc_config = True
					header_rpc_config += CODE_FORMAT.RPC_CONFIG_BODY.format(
						method['rpc_config']['rpc_mode'],
						method['rpc_config']['transfer_mode'],
						method['rpc_config']['call_local'],
						method['rpc_config']['channel'],
						method[\"name\"]
						)
			else:
				args_list = CODE_FORMAT.expand_property_info_list(method['varargs'])

				Hvaragr_method += CODE_FORMAT.VARARG_REGISTER.format(
					class_name,
					method[\"name\"],
					method[\"bind_name\"],
					'\\n' + args_list + '\\n\\t\\t'
		 				if args_list != '' else '')

		prev_group, prev_subgroup = '', ''
		for prop in content['properties']:
			if prop['getter'] not in methods_list:
				Hmethod += CODE_FORMAT.METHOD_REGISTER.format(
					class_name,
					prop[\"getter\"],
					prop[\"getter\"],
					'',
					''
					)
				property_set_get_defs += CODE_FORMAT.GENERATE_GETTER.format(
					class_name_full,
					prop[\"getter\"],
					prop[\"name\"],
					prop[\"type\"]
					)
				gen_getters.append([prop[\"getter\"], prop[\"name\"]])

			if prop['setter'] not in methods_list:
				Hmethod += CODE_FORMAT.METHOD_REGISTER.format(
					class_name,
					prop[\"setter\"],
					prop[\"setter\"],
					', \"value\"',
					''
					)
				property_set_get_defs += CODE_FORMAT.GENERATE_SETTER.format(
					class_name_full,
					prop[\"setter\"],
					prop[\"name\"],
					prop[\"type\"]
					)
				gen_setters.append([prop[\"setter\"], prop[\"name\"]])

			group, subgroup = prop['group'], prop['subgroup']
			group_ = group_name(group)
			if group != '' and group != prev_group:
				Hprop += CODE_FORMAT.ADD_GROUP.format(group, group_)
				prev_group = group

			subgroup_ = group_name(subgroup)
			if subgroup != '' and subgroup != prev_subgroup:
				Hprop += CODE_FORMAT.ADD_SUBGROUP.format(subgroup, subgroup_)
				prev_subgroup = subgroup

			prop_name = group_ + subgroup_ + prop['name']
			hints = CODE_FORMAT.PROPERTY_HINTS.format(prop[\"hint\"], prop[\"args\"]) if prop['hint'] != None else ''
			Hprop += CODE_FORMAT.ADD_PROPERTY.format(
				CODE_FORMAT.PROPERTY_INFO.format(f'decltype({prop[\"name\"]})', prop_name, hints),
				prop[\"setter\"],
				prop[\"getter\"]
				)

		defs[class_name_full]['gen_setters'] = gen_setters
		defs[class_name_full]['gen_getters'] = gen_getters

		for signal_name, args in content['signals']:
			args_str = '\\n'.join('\\t\\t,' + CODE_FORMAT.PROPERTY_INFO.format(arg_type, arg_name, '')
				for arg_type, arg_name in args)
			Hsignal += CODE_FORMAT.ADD_SIGNAL.format(
				signal_name,
				'\\n' + args_str + '\\n\\t\\t' if args_str != '' else ''
				)

		for enum, consts in content['enum_constants'].items():
			outside_bind += CODE_FORMAT.VARIANT_ENUM_CAST.format(enum)
			for const in consts:
				Henum += CODE_FORMAT.BIND_ENUM_CONSTANT.format(const)

		for enum, consts in content['bitfields'].items():
			outside_bind += CODE_FORMAT.VARIANT_BITFIELD_CAST.format(enum)
			for const in consts:
				Hbitfield += CODE_FORMAT.BIND_BITFIELD_FLAG.format(const)

		for const in content['constants']:
			Hconst += CODE_FORMAT.BIND_CONSTANT.format(const)

		if 'is_resource_loader' in content:
			variable_name = content[\"class_name\"] + '_loader'
			global_variables.append(f'Ref<{class_name_full}> {variable_name};')
		elif 'is_resource_saver' in content:
			variable_name = content[\"class_name\"] + '_saver'
			global_variables.append(f'Ref<{class_name_full}> {variable_name};')
		elif 'is_singleton' in content:
			global_variables.append(f'{content[\"class_name\"]}* {content[\"class_name\"]}_singleton_ptr;')

		for type, name, init in content['static_members']:
			global_variables.append(f'alignas({type}) char {class_name_full}::{name + \"_impl\"}[] = {{0}};')

		header_rpc_config = 'void {}::_rpc_config() {{{}}}\\n'.format(
				class_name_full, '\\n' + header_rpc_config if header_rpc_config != '' else '')
		header_bind_methods = '\\n\\n'.join(i for i in [Hmethod, Hvirtual_method, Hstatic_method, Hvaragr_method, Hprop, Hsignal, Henum, Hbitfield, Hconst] if i != '')
		header_bind_methods = content['bind_methods_prepend'] + header_bind_methods + content['bind_methods_append']

		header_defs += [f'// {class_name_full} : {content[\"base\"]}\\n',
			'void {}::_bind_methods() {{{}}}\\n'.format(
			class_name_full, '\\n' + header_bind_methods if header_bind_methods != '' else ''),
			header_rpc_config] + \\
			([property_set_get_defs] if property_set_get_defs != '' else []) + \\
			([outside_bind] if outside_bind != '' else [])

	gen_filename = filename_to_gen_filename(file, env)
	content = ''
	if len(defs) != 0:
		header_include = '#include <cppscript_bindings.h>\\n\\n#include \"{}\"\\n\\nusing namespace godot;\\n\\n{}' \\
				.format(
					os.path.relpath(file, os.path.dirname(gen_filename)).replace('\\\\', '/'),
					('\\n'.join(global_variables) + '\\n\\n' if global_variables != [] else ''))

		if has_rpc_config != '':
			header_include = '#include <godot_cpp/classes/multiplayer_api.hpp>\\n' + header_include
			header_include = '#include <godot_cpp/classes/multiplayer_peer.hpp>\\n' + header_include

		content = CODE_FORMAT.DONOTEDIT_MSG + header_include + '\\n'.join(header_defs)

	os.makedirs(os.path.dirname(gen_filename), exist_ok=True)
	with open(gen_filename, 'w') as fileopen:
		fileopen.write(content)


def write_register_header(defs_all, env):
	CODE_FORMAT = env['code_format']
	target = os.path.join(env['header_dir'], 'scripts.gen.h')
	scripts_header = CODE_FORMAT.DONOTEDIT_MSG
	classes_register_levels = {name[12:] : [] for name in INIT_LEVELS}
	static_members_levels = {name[12:] : [] for name in INIT_LEVELS}

	loaders_savers = []
	has_singleton = False
	def make_register_str_pair(class_name_full, content):
		register_str = CODE_FORMAT.REGISTER_CLASS.format(content['type'], class_name_full)
		unregister_str = ''

		static_members_levels[content['init_level']] += \\
			[(type, f'{class_name_full}::{name}', init) for type, name, init in content['static_members']]

		if 'is_resource_loader' in content:
			variable_name = f'{content[\"class_name\"]}_loader'

			loaders_savers.append(f'extern Ref<{class_name_full}> {variable_name};')
			register_str += f'\\t{variable_name}.instantiate();\\n\\tResourceLoader::get_singleton()->add_resource_format_loader({variable_name});\\n'
			unregister_str += f'\\tResourceLoader::get_singleton()->remove_resource_format_loader({variable_name});\\n\\t{variable_name}.unref();\\n'

		elif 'is_resource_saver' in content:
			variable_name = f'{content[\"class_name\"]}_saver'

			loaders_savers.append(f'extern Ref<{class_name_full}> {variable_name};\\n')
			register_str += f'\\t{variable_name}.instantiate();\\n\\tResourceSaver::get_singleton()->add_resource_format_saver({variable_name});\\n'
			unregister_str += f'\\tResourceSaver::get_singleton()->remove_resource_format_saver({variable_name});\\n\\t{variable_name}.unref();\\n'

		elif 'is_editor_plugin' in content:
			register_str += f'\\tEditorPlugins::add_by_type<{class_name_full}>();\\n'

		elif 'is_singleton' in content:
			nonlocal has_singleton
			has_singleton = True
			loaders_savers.append(f'extern {content[\"class_name\"]}* {content[\"class_name\"]}_singleton_ptr;')
			register_str += f'\\t{content[\"class_name\"]}_singleton_ptr = memnew({class_name_full});\\n\\tEngine::get_singleton()->register_singleton(\"{content[\"class_name\"]}\", {content[\"class_name\"]}_singleton_ptr);\\n'
			unregister_str += f'\\tEngine::get_singleton()->unregister_singleton(\"{content[\"class_name\"]}\");\\n\\tmemdelete({content[\"class_name\"]}_singleton_ptr);\\n'

		return register_str, unregister_str

	for file, filecontent in defs_all['files'].items():
		classes = filecontent['content']
		if len(classes) == 0:
			continue

		scripts_header += '#include <cppscript_bindings.h>\\n'
		scripts_header += '#include \"{}\"\\n'.format(os.path.relpath(file, os.path.dirname(target)).replace('\\\\', '/'))

		for class_name_full, content in classes.items():
			# Ensure parent classes are registered before children
			# by iterating throught pairs of (base_name, register_str)
			classes_register = classes_register_levels[content['init_level']]
			class_name, base = content['class_name'], content['base']
			dots = base.rfind(':')
			base = base if dots == -1 else base[dots+1:]
			for i in range(len(classes_register)):
				if class_name == classes_register[i][0]:
					classes_register.insert(i, (base, make_register_str_pair(class_name_full, content)))
					break
			else:
				classes_register.append((base, make_register_str_pair(class_name_full, content)))


	if loaders_savers != []:
		scripts_header += '#include <godot_cpp/classes/resource_loader.hpp>\\n'
		scripts_header += '#include <godot_cpp/classes/resource_saver.hpp>\\n'

	if has_singleton:
		scripts_header += '#include <godot_cpp/classes/engine.hpp>\\n'

	classes_register_str = ''
	static_members_init_deinit_str = ''
	if classes_register_levels['CORE'] != []:
		minimal_register_level = 'MODULE_INITIALIZATION_LEVEL_CORE'
	elif classes_register_levels['SERVERS'] != []:
		minimal_register_level = 'MODULE_INITIALIZATION_LEVEL_SERVERS'
	else:
		minimal_register_level = 'MODULE_INITIALIZATION_LEVEL_SCENE'

	scripts_header += '\\nusing namespace godot;\\n\\n' + \\
			f'static const ModuleInitializationLevel DEFAULT_INIT_LEVEL = {minimal_register_level};\\n\\n' + \\
			('\\n'.join(loaders_savers) + '\\n\\n' if loaders_savers != [] else '')

	for level_name, defs in classes_register_levels.items():
		registers = ''.join(i[0] for _, i in defs) + f'\\timpl::StaticAccess::_init_static_members_level_{level_name.lower()}();\\n'
		unregisters = ''.join(i[1] for _, i in defs) + f'\\timpl::StaticAccess::_uninit_static_members_level_{level_name.lower()}();\\n'

		static_members_init = ''.join(
				f'\\t\\tnew (\"\", &{name}, sizeof({type}), \"\") {type}({init});\\n'
				#f'\\t\\tmemnew_placement(&{name}, {type}({init}));\\n'
				for type, name, init in static_members_levels[level_name])
		static_members_deinit = ''.join(f'\\t\\timpl::destroy_object({name});\\n' for type, name, init in static_members_levels[level_name])

		static_members_init_deinit_str += '\\tstatic _FORCE_INLINE_ void _init_static_members_level_{}() {{{}}}\\n\\n'.format(
			level_name.lower(), '\\n' + static_members_init + '\\t' if static_members_init != '' else '')

		static_members_init_deinit_str += '\\tstatic _FORCE_INLINE_ void _uninit_static_members_level_{}() {{{}}}\\n\\n'.format(
			level_name.lower(), '\\n' + static_members_deinit + '\\t' if static_members_deinit != '' else '')

		classes_register_str += '_FORCE_INLINE_ void _register_level_{}() {{{}}}\\n\\n'.format(
			level_name.lower(), '\\n' + registers)

		classes_register_str += '_FORCE_INLINE_ void _unregister_level_{}() {{{}}}\\n\\n'.format(
			level_name.lower(), '\\n' + unregisters)

	static_members_init_deinit_str = CODE_FORMAT.STATIC_ACCESS_CLASS_BODY.format(static_members_init_deinit_str)
	scripts_header += static_members_init_deinit_str + classes_register_str

	new_hash = hashlib.md5(scripts_header.encode()).hexdigest()

	if new_hash != defs_all['hash']:
		with open(target, 'w') as file:
			file.write(scripts_header)
		defs_all['hash'] = new_hash

		return True

	return False


def write_property_header(new_defs, env):
	CODE_FORMAT = env['code_format']
	filepath = os.path.join(env['header_dir'], 'properties.gen.h')
	body = CODE_FORMAT.DONOTEDIT_MSG
	for filename, filecontent in new_defs['files'].items():
		classcontent = filecontent['content']
		for class_name_full, content in classcontent.items():
			gen_setgets = [
				' \\\\\\n' + CODE_FORMAT.GENERATE_GETTER_DECLARATION.format(method, next(prop['type'] for prop in content['properties'] if prop['name'] == property))
					for method, property in content['gen_getters']] + [
				' \\\\\\n' + CODE_FORMAT.GENERATE_SETTER_DECLARATION.format(method, next(prop['type'] for prop in content['properties'] if prop['name'] == property))
					for method, property in content['gen_setters']]

			body += f'#define GSETGET_{content[\"class_name\"]}' + ''.join(gen_setgets) + '\\n\\n'

	with open(filepath, 'w') as file:
		file.write(body)



if __name__ == \"__main__\":
    # Ran as bindings generator

    import argparse, os, sys

    parser = argparse.ArgumentParser(
            prog='cppscript_bindings',
            description='Generates C++ bindings code for GDExtension')

    parser.add_argument('--header-name', type=str, nargs=1, required=True)
    parser.add_argument('--header-dir', type=str, nargs=1, required=True)
    parser.add_argument('--gen-dir', type=str, nargs=1, required=True)
    parser.add_argument('--auto-methods', type=bool, default=True)
    parser.add_argument('--definitions', type=str, nargs='*')
    parser.add_argument('--include-paths', type=str, nargs='*')
    parser.add_argument('sources', nargs='*')

    args = parser.parse_args(sys.argv[1:])
    env = {
        'header_name' : args.header_name[0],
        'header_dir' : args.header_dir[0],
        'gen_dir' : args.gen_dir[0],
        'compile_defs' : set(args.definitions),
        'include_paths' :  set(args.include_paths),
        'auto_methods' : args.auto_methods,
        'code_format' : code_format_godot_cpp()
            if os.getenv(\"CPPSCRIPT_NO_CONSTEXPR_CHECKS\", False)
            else code_format_cppscript_constexr_checks()
        }

    sys.exit(generate_header_cmake(args.sources, env))

"
)


#TODO: make it work in parallel
function(create_cppscript_target)
	set(options AUTO_METHODS)
	set(oneValueArgs HEADER_NAME HEADERS_DIR GEN_DIR OUTPUT_SOURCES)
	set(multiValueArgs HEADERS_LIST COMPILE_DEFS INCLUDE_PATHS)
	cmake_parse_arguments(CPPS "${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

	# Handle required args and empty/NOTFOUND lists
	if(NOT CPPS_HEADER_NAME)
		message(FATAL_ERROR "Header name is required argument (for example: `HEADER_NAME project_name.h`)")
	endif()

	if(NOT CPPS_HEADERS_DIR)
		message(FATAL_ERROR "Headers directory is required argument (for example: `HEADERS_DIR \${CMAKE_CURRENT_SOURCE_DIR}/include`)")
	endif()
	
	if(NOT CPPS_OUTPUT_SOURCES)
		message(FATAL_ERROR "Output sources is required argument (for example: `OUTPUT_SOURCES GEN_SOURCES`)")
	endif()

	if(NOT CPPS_GEN_DIR)
		set(CPPS_GEN_DIR "${CMAKE_CURRENT_BINARY_DIR}/.cppscript.gen")
	endif()
	
	if(NOT CPPS_HEADERS_LIST)
		set(CPPS_HEADERS_LIST "")
	endif()
	
	if(NOT CPPS_COMPILE_DEFS)
		set(CPPS_COMPILE_DEFS "")
	endif()
	
	if(NOT CPPS_INCLUDE_PATHS)
		set(CPPS_INCLUDE_PATHS "")
	endif()

	if(CPPS_AUTO_METHODS)
		set(AUTO_METHODS_STR "True")
	else()
		set(AUTO_METHODS_STR "False")
	endif()

    # Generate python script and headers
    set(GODOT_CPPSCRIPT_PY_SCRIPT_PATH "${CMAKE_CURRENT_BINARY_DIR}/cppscript.py")
	 set(GODOT_CPPSCRIPT_DEFS_H_PATH "${CPPS_HEADERS_DIR}/cppscript_defs.h")
    set(GODOT_CPPSCRIPT_BINDINGS_H_PATH "${CPPS_HEADERS_DIR}/cppscript_bindings.h")
	 set(GODOT_CPPSCRIPT_H_PATH "${CPPS_HEADERS_DIR}/${CPPS_HEADER_NAME}")

    file(WRITE "${GODOT_CPPSCRIPT_PY_SCRIPT_PATH}" "${CPPSCRIPT_EMBED_PY_SCRIPT}")
    file(WRITE "${GODOT_CPPSCRIPT_DEFS_H_PATH}" "${CPPSCRIPT_DEFS_H}")
    file(WRITE "${GODOT_CPPSCRIPT_BINDINGS_H_PATH}" "${CPPSCRIPT_BINDINGS_H}")

	 string(TOUPPER "${CPPS_HEADER_NAME}" H_GUARD_STR)
	 string(REPLACE "." "_" H_GUARD_STR "${H_GUARD_STR}")
	 string(REPLACE "@H_GUARD@" "${H_GUARD_STR}" CPPSCRIPT_BODY_H_FORMATTED "${CPPSCRIPT_BODY_H}") 
	 file(WRITE "${GODOT_CPPSCRIPT_H_PATH}" "${CPPSCRIPT_BODY_H_FORMATTED}")

	foreach(PATH ${CPPS_HEADERS_LIST})
		file(RELATIVE_PATH PATH "${CPPS_HEADERS_DIR}" "${PATH}")
		string(REGEX REPLACE "\.[^./\\]+$" ".gen.cpp" relative_path "${PATH}")
		list(APPEND SOURCES_LIST "${CPPS_GEN_DIR}/${relative_path}")
	endforeach()

	add_custom_command(
		OUTPUT
			${CPPS_HEADERS_DIR}/${CPPS_HEADER_NAME}
			${CPPS_HEADERS_DIR}/scripts.gen.h
			${CPPS_HEADERS_DIR}/properties.gen.h
			${SOURCES_LIST}

		COMMAND
			${Python3_EXECUTABLE} "${GODOT_CPPSCRIPT_PY_SCRIPT_PATH}"
				"--header-name" "${CPPS_HEADER_NAME}"
				"--header-dir" "${CPPS_HEADERS_DIR}"
				"--gen-dir" "${CPPS_GEN_DIR}"
				"--auto-methods" "${AUTO_METHODS_STR}"
				"--definitions" ${CPPS_COMPILE_DEFS}
				"--include-paths" ${CPPS_HEADERS_DIR} ${CPPS_INCLUDE_PATHS}
				"--"
				${CPPS_HEADERS_LIST}

		DEPENDS ${CPPS_HEADERS_LIST}
		WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
		VERBATIM
		COMMAND_EXPAND_LISTS
		COMMENT "Parsing header files..."
	)
	set(${CPPS_OUTPUT_SOURCES} "${SOURCES_LIST}" PARENT_SCOPE)
endfunction()

endif()
