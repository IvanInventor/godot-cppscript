#ifndef CPPSCRIPT_H
#define CPPSCRIPT_H

#include <godot_cpp/classes/multiplayer_api.hpp>
#include <godot_cpp/classes/multiplayer_peer.hpp>


#define GCLASS(CLASS_NAME, CLASS_NAME_INH) 								\
	GDCLASS(CLASS_NAME , CLASS_NAME_INH)								\
public:													\
static void _bind_methods();										\
void _rpc_config();											\
		template<auto P>									\
	decltype(getPointerType(P)) _cppscript_getter() {						\
		return this->*P;									\
	}												\
	template<auto P>										\
	void _cppscript_setter(decltype(getPointerType(P)) new_value) {					\
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

template <class C, typename T>
T getPointerType(T C::*v);

#endif // CPPSCRIPT_H
