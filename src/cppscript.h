#ifndef CPPSCRIPT_H
#define CPPSCRIPT_H
#include "properties.gen.h"
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


namespace impl {

template <typename T, typename = void>
struct is_defined : std::false_type {};

template <typename T>
struct is_defined<T, std::void_t<decltype(T::VARIANT_TYPE)>> : std::true_type {};

template<class T>
static constexpr bool is_supported_type = is_defined<godot::GetTypeInfo<T>>::value;


template<class T>
struct is_supported : std::integral_constant<bool, is_supported_type<T>> {
	static_assert(is_supported_type<T>, "Type not supported. If it's your custom class, maybe you forgot to register it with GCLASS()");
};



template<class T>
static constexpr bool is_ret_supported = is_supported<T>::value;

template<>
static constexpr bool is_ret_supported<void> = true;

template <typename>
struct MemberSignature;

template <typename Class, typename Ret, typename... Args>
struct MemberSignature<Ret (Class::*)(Args...) const> {
	using ret_t = Ret;
	static constexpr bool value = (is_ret_supported<Ret> && (is_supported<Args>::value && ...));
};

template <typename Class, typename Ret, typename... Args>
struct MemberSignature<Ret (Class::*)(Args...)> {
	using ret_t = Ret;
	static constexpr bool value = (is_ret_supported<Ret> && (is_supported<Args>::value && ...));
};

template <typename Ret, typename... Args>
struct FunctionSignature;

template <typename Ret, typename... Args>
struct FunctionSignature<Ret (*)(Args...)> {
	static constexpr bool value = is_ret_supported<Ret> && (is_supported<Args>::value && ...);
};


template <typename Class, typename Ret, typename... Args>
constexpr auto is_method_signature_supported(Ret (Class::*func)(Args...) const) {
    return MemberSignature<decltype(func)>();
}

template <typename Class, typename Ret, typename... Args>
constexpr auto is_method_signature_supported(Ret (Class::*func)(Args...)) {
    return MemberSignature<decltype(func)>();
}

template <typename Ret, typename... Args>
constexpr auto is_function_signature_supported(Ret (*func)(Args...)) {
	return FunctionSignature<decltype(func)>();
}


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

};

template<class T, class ...Args>
godot::PropertyInfo MakePropertyInfo(Args&&... args) {
	static_assert(impl::is_supported<T>::value, "Property of this type is not supported");
	return impl::BindCheck<impl::is_supported<T>::value>::template MakePropertyInfo<T>(std::forward<Args>(args)...);
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

	template<class Name_t, class DMETHOD_t, class ...Args>
	static _FORCE_INLINE_ void bind(Name_t name, DMETHOD_t dmethod, Args... args) {
		impl::BindCheck<is_supported>::bind_static(name, dmethod, Ptr, args...);	
	}
};
#endif // CPPSCRIPT_H
