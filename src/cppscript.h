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
#define GIGNORE(...)

