#ifndef CPPSCRIPT_HEADER
#define CPPSCRIPT_HEADER
#include <godot_cpp/classes/multiplayer_api.hpp>
#include <godot_cpp/classes/multiplayer_peer.hpp>


#define GCLASS(CLASS_NAME, CLASS_NAME_INH) 								\
	GDCLASS(CLASS_NAME , CLASS_NAME_INH)								\
protected:												\
static void _bind_methods();										\
protected:												\
void _rpc_config();											\
public:													\
GSETGET_ ## CLASS_NAME											\
private:

#define GVIRTUAL_CLASS(CLASS_NAME, CLASS_NAME_INH) GCLASS(CLASS_NAME, CLASS_NAME_INH)
#define GABSTRACT_CLASS(CLASS_NAME, CLASS_NAME_INH) GCLASS(CLASS_NAME, CLASS_NAME_INH)
#define GINTERNAL_CLASS(CLASS_NAME, CLASS_NAME_INH) GCLASS(CLASS_NAME, CLASS_NAME_INH)

#define GENERATE_GETTER_DECLARATION(function, property)	\
decltype(property) function();

#define GENERATE_SETTER_DECLARATION(function, property)	\
void function(decltype(property));

#define GENERATE_GETTER(function, property)	\
decltype(property) function() {			\
	return property;			\
}

#define GENERATE_SETTER(function, property)	\
void function(decltype(property) value) {	\
	this->property = value;			\
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

#endif // CPPSCRIPT_HEADER
