#include <godot_cpp/classes/multiplayer_api.hpp>
#include <godot_cpp/classes/multiplayer_peer.hpp>


#define REGISTER_CLASS_GEN_CODE(CLASS_NAME) REGISTER_CLASS_GEN_CODE_CLASS_ ## CLASS_NAME
#define STR(s) # s
#define EXPORT_METHOD(METHOD_NAME, ...)

#define GCLASS(CLASS_NAME, CLASS_NAME_INH) 								\
	GDCLASS(CLASS_NAME , CLASS_NAME_INH)								\
public:													\
static void _bind_methods();										\
void _rpc_config();											\
	template<auto P, class T>									\
	T _cppscript_getter() {										\
		return this->*P;									\
	}												\
	template<auto P, class T>									\
	void _cppscript_setter(T new_value) {								\
		this->*P = new_value;									\
	}
#define GVIRTUAL_CLASS(CLASS_NAME, CLASS_NAME_INH) GCLASS(CLASS_NAME, CLASS_NAME_INH)
#define GABSTRACT_CLASS(CLASS_NAME, CLASS_NAME_INH) GCLASS(CLASS_NAME, CLASS_NAME_INH)

#define GPROPERTY(...)
#define GMETHOD(...)
#define GGROUP(...)
#define GSUBGROUP(...)
#define GCONSTANT(...)
#define GBITFIELD(...)
#define GSIGNAL(...)
#define GRPC(...)
#define GVARARG(...)

#define GEXPORT_NONE(...)
#define GEXPORT_RANGE(...)
#define GEXPORT_ENUM(...)
#define GEXPORT_ENUM_SUGGESTION(...)
#define GEXPORT_EXP_EASING(...)
#define GEXPORT_LINK(...)
#define GEXPORT_FLAGS(...)
#define GEXPORT_LAYERS_2D_RENDER(...)
#define GEXPORT_LAYERS_2D_PHYSICS(...)
#define GEXPORT_LAYERS_2D_NAVIGATION(...)
#define GEXPORT_LAYERS_3D_RENDER(...)
#define GEXPORT_LAYERS_3D_PHYSICS(...)
#define GEXPORT_LAYERS_3D_NAVIGATION(...)
#define GEXPORT_FILE(...)
#define GEXPORT_DIR(...)
#define GEXPORT_GLOBAL_FILE(...)
#define GEXPORT_GLOBAL_DIR(...)
#define GEXPORT_RESOURCE_TYPE(...)
#define GEXPORT_MULTILINE_TEXT(...)
#define GEXPORT_EXPRESSION(...)
#define GEXPORT_PLACEHOLDER_TEXT(...)
#define GEXPORT_COLOR_NO_ALPHA(...)
#define GEXPORT_OBJECT_ID(...)
#define GEXPORT_TYPE_STRING(...)
#define GEXPORT_NODE_PATH_TO_EDITED_NODE(...)
#define GEXPORT_OBJECT_TOO_BIG(...)
#define GEXPORT_NODE_PATH_VALID_TYPES(...)
#define GEXPORT_SAVE_FILE(...)
#define GEXPORT_GLOBAL_SAVE_FILE(...)
#define GEXPORT_INT_IS_OBJECTID(...)
#define GEXPORT_INT_IS_POINTER(...)
#define GEXPORT_ARRAY_TYPE(...)
#define GEXPORT_LOCALE_ID(...)
#define GEXPORT_LOCALIZABLE_STRING(...)
#define GEXPORT_NODE_TYPE(...)
#define GEXPORT_HIDE_QUATERNION_EDIT(...)
#define GEXPORT_PASSWORD(...)
