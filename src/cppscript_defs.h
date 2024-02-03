#ifndef CPPSCRIPT_HEADER
#define CPPSCRIPT_HEADER

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
#define GEDITOR_PLUGIN(...)
#define GSINGLETON(...);

#define GSTATIC_MEMBER(s_type, s_name, ...)												\
friend impl::StaticAccess;																		\
alignas(s_type) static char s_name ## _impl [sizeof(s_type)];						\
static inline s_type& s_name = *reinterpret_cast<s_type*>(&s_name ## _impl);

namespace impl {
struct StaticAccess;
};
#endif // CPPSCRIPT_HEADER
