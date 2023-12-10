#ifndef CPPSCRIPT_BINDINGS_H
#define CPPSCRIPT_BINDINGS_H

#include <type_traits>
#include <godot_cpp/core/class_db.hpp>
#include <godot_cpp/classes/ref.hpp>
#include <godot_cpp/classes/resource.hpp>


namespace impl {

template <typename T, typename = void>
struct is_defined : std::false_type {};

template <typename T>
struct is_defined<T, std::void_t<decltype(T::VARIANT_TYPE)>> : std::true_type {};

template<class T>
static constexpr bool is_supported_type_v = is_defined<godot::GetTypeInfo<T>>::value;


template<class T>
struct assert_is_supported_type : std::integral_constant<bool, is_supported_type_v<T>> {
	static_assert(is_supported_type_v<T>, "Type not supported. If it's your custom class, either it had complilation errors, or maybe you forgot to register it with GCLASS()");
};

template<class T>
static constexpr bool assert_is_supported_type_v = assert_is_supported_type<T>::value;


template<class T>
static constexpr bool assert_is_ret_supported = assert_is_supported_type_v<T>;

template<>
static constexpr bool assert_is_ret_supported<void> = true;

template <typename>
struct MemberSignature;

template <typename Class, typename Ret, typename... Args>
struct MemberSignature<Ret (Class::*)(Args...) const> {
	static constexpr bool value = assert_is_ret_supported<Ret> && (assert_is_supported_type_v<Args> && ...);
};

template <typename Class, typename Ret, typename... Args>
struct MemberSignature<Ret (Class::*)(Args...)> {
	static constexpr bool value = assert_is_ret_supported<Ret> && (assert_is_supported_type_v<Args> && ...);
};

template <typename Ret, typename... Args>
struct FunctionSignature;

template <typename Ret, typename... Args>
struct FunctionSignature<Ret (*)(Args...)> {
	static constexpr bool value = assert_is_ret_supported<Ret> && (assert_is_supported_type_v<Args> && ...);
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

};

template<class T, class ...Args>
_FORCE_INLINE_ godot::PropertyInfo MakePropertyInfo(Args&&... args) {
	static_assert(impl::assert_is_supported_type_v<T>, "Property of this type is not supported");
	
	using IsResource = impl::IsResourceProperty<T>;
	if constexpr(sizeof...(Args) == 1 && IsResource::value) {
		return impl::BindCheck<impl::assert_is_supported_type_v<T>>::template MakePropertyInfo<T>(std::forward<Args>(args)..., godot::PROPERTY_HINT_RESOURCE_TYPE, IsResource::type::get_class_static());
	} else {
		return impl::BindCheck<impl::assert_is_supported_type_v<T>>::template MakePropertyInfo<T>(std::forward<Args>(args)...);
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
