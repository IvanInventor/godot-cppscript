#ifndef CPPSCRIPT_H
#define CPPSCRIPT_H
#include <properties.gen.h>
#include <godot_cpp/classes/multiplayer_api.hpp>
#include <godot_cpp/classes/multiplayer_peer.hpp>


#define GCLASS(CLASS_NAME, CLASS_NAME_INH) 								\
	GDCLASS(CLASS_NAME , CLASS_NAME_INH)								\
protected:												\
static void _bind_methods();										\
protected:												\
void _rpc_config();											\
public:													\
GSETGET_ ## CLASS_NAME ## _ ## CLASS_NAME_INH						\
private:

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

#endif // CPPSCRIPT_H
