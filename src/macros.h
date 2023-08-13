#define REGISTER_CLASS_GEN_CODE(CLASS_NAME) REGISTER_CLASS_GEN_CODE_CLASS_ ## CLASS_NAME
#define STR(s) # s
#define EXPORT_METHOD(METHOD_NAME, ...)

#define GCLASS(CLASS_NAME, CLASS_NAME_INH) 						\
	GDCLASS(CLASS_NAME , CLASS_NAME_INH)			\
public:								\
static void _bind_methods();

#define GPROPERTY(...)
#define GMETHOD(...)
#define GGROUP(...)
#define GSUBGROUP(...)
#define GCONSTANT(...)
#define GBITFIELD(...)
