import os

# (...) explains arguments for .format(...) call

class code_format_godot_cpp:
	DONOTEDIT_MSG = "/*-- GENERATED FILE - DO NOT EDIT --*/\n\n"

	# (header_guard)
	CPPSCRIPT_BODY = DONOTEDIT_MSG + \
"""#ifndef {0}
#define {0}
#include <cppscript_defs.h>
#include "properties.gen.h"
#endif // {0}
"""

	# (rpc_mode, transfer_mode, call_local, method_name)
	RPC_CONFIG_BODY = \
"""	{{
	Dictionary opts;
	opts["rpc_mode"] = MultiplayerAPI::{0};
	opts["transfer_mode"] = MultiplayerPeer::{1};
	opts["call_local"] = {2};
	opts["channel"] = {3};
	rpc_config("{4}", opts);
	}}
"""
	
	# (code)
	STATIC_ACCESS_CLASS_BODY = \
"""namespace impl {{
struct StaticAccess {{
{}}};
}};

"""

	# (type, name, args)
	PROPERTY_INFO = 'PropertyInfo(GetTypeInfo<{0}>::VARIANT_TYPE, "{1}"{2})'

	# (value)
	ARGNAMES_SEPARATOR = ', "{0}"'

	# (value)
	DEFAULT_VALUES_SEPARATOR = ', DEFVAL({0})'

	# (class_name, method_name, method_bind_name, args, default_values)
	METHOD_REGISTER = '\tClassDB::bind_method(D_METHOD("{2}"{3}), &{0}::{1}{4});\n'

	# (class_name, method_name, method_bind_name, args, default_values)
	STATIC_METHOD_REGISTER = '\tClassDB::bind_static_method(get_class_static(), D_METHOD("{2}"{3}),	&{0}::{1}{4});\n'

	@classmethod
	def expand_property_info_list(cls, args):
		return '\n'.join(f'\t\tmi.arguments.push_back({cls.PROPERTY_INFO.format(type, name, "")});' for type, name in args)

	# (class_name, method_name, method_bind_name, property_list)
	VARARG_REGISTER = \
"""	{{
		MethodInfo mi;
{3}
		mi.name = "{2}";
		ClassDB::bind_vararg_method(METHOD_FLAGS_DEFAULT, "{2}", &{0}::{1}, mi);
	}}
"""

	# (class_name_full, method_name, property_name)
	GENERATE_GETTER = 'GENERATE_GETTER({0}::{1}, {0}::{2});\n'

	# (method_name, property_name)
	GENERATE_GETTER_DECLARATION = 'GENERATE_GETTER_DECLARATION({0}, {1})'

	# (class_name_full, method_name, property_name)
	GENERATE_SETTER = 'GENERATE_SETTER({0}::{1}, {0}::{2});\n'
 	
	# (method_name, property_name)
	GENERATE_SETTER_DECLARATION = 'GENERATE_SETTER_DECLARATION({0}, {1})'

	# (group_name, groug_name_expanded)
	ADD_GROUP = '\tADD_GROUP("{0}", "{1}");\n'
 
	# (subgroup_name, subgroug_name_expanded)
	ADD_SUBGROUP = '\tADD_SUBGROUP("{0}", "{1}");\n'
 
 	# (hint, other_args)
	PROPERTY_HINTS = ', {0}, {1}'

 	# (property_info, setter, getter)
	ADD_PROPERTY = '\t\tADD_PROPERTY({0}, "{1}", "{2}");\n'

	# (signal_name, property_info_list)
	ADD_SIGNAL = '\tADD_SIGNAL(MethodInfo("{0}"{1}));\n'

	# (name)
	VARIANT_ENUM_CAST = 'VARIANT_ENUM_CAST({0});\n'
	
	# (name)
	BIND_ENUM_CONSTANT = '\tBIND_ENUM_CONSTANT({0});\n'

 	# (name)
	VARIANT_BITFIELD_CAST = 'VARIANT_BITFIELD_CAST({0});\n'

	# (name)
	BIND_BITFIELD_FLAG = '\tBIND_BITFIELD_FLAG({0});\n'

	# (name)
	BIND_CONSTANT = '\tBIND_CONSTANT({0});\n'

	#(CLASS_TYPE, class_name)
	REGISTER_CLASS = '\tGDREGISTER_{0}({1});\n'


class code_format_cppscript_constexr_checks(code_format_godot_cpp):
	# (type, name, args)
	PROPERTY_INFO = 'MakePropertyInfo<{0}>("{1}"{2})'

	@classmethod
	def expand_property_info_list(cls, args):
		return '\n'.join(f'\t\t,' + cls.PROPERTY_INFO.format(type, name, '') for type, name in args)

	# (class_name, method_name, method_bind_name, args, default_values)
	METHOD_REGISTER = '\tMethod<&{0}::{1}>::bind(D_METHOD("{2}"{3}){4});\n'

	# (class_name, method_name, method_bind_name, args, default_values)
	STATIC_METHOD_REGISTER = '\tStaticMethod<&{0}::{1}>::bind(get_class_static(), D_METHOD("{2}"{3}){4});\n'

	# (class_name, method_name, method_bind_name, property_list)
	VARARG_REGISTER = '\tMethod<&{0}::{1}>::bind_vararg("{2}"{3});\n'


CODE_FORMAT = code_format_godot_cpp() \
	if os.getenv("CPPSCRIPT_NO_CONSTEXPR_CHECKS", False) \
		else code_format_cppscript_constexr_checks() 

