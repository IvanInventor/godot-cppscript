# godot-cpp-script

Python script that implements various C++ macros to automate binding code generation. Used as SCons custom builder besides default library builder. Works similar to [Unreal Header Tool](https://docs.unrealengine.com/5.3/en-US/unreal-header-tool-for-unreal-engine/).

[Example project](https://github.com/IvanInventor/godot-cppscript-example)

[Keywords description](https://github.com/IvanInventor/godot-cppscript-example/blob/master/src/example.hpp) (read comments)

[Property hints description](https://github.com/IvanInventor/godot-cppscript-example/blob/master/src/example_properties.hpp) (read comments)
## Dependencies
#### Programs
[Godot 4](https://godotengine.org/download/archive/) (>=4.1)

[Requirements](https://docs.godotengine.org/en/stable/contributing/development/compiling/index.html#building-for-target-platforms) from official guide for your OS



#### Python dependencies
libclang
```bash
pip install libclang
```
## Installation

### As project submodule

- From root of your project (git initialized)
```bash
git submodule add https://github.com/IvanInventor/godot-cpp-script cppscript
git submodule update --recursive --init cppscript
```
- Checkout your version of godot
    - For stable releases: checkout one of [tags](https://github.com/godotengine/godot-cpp/tags)
    ```bash
    cd cppscript/godot-cpp/
    git checkout <tag>
    ```
    - For custom builds (from [guide](https://docs.godotengine.org/en/stable/tutorials/scripting/gdextension/gdextension_cpp_example.html#building-the-c-bindings)):
    ```bash
    # switch to branch corresponding to godot version
    # Godot 4.1.3 -> 4.1
    cd cppscript/godot-cpp/
    git pull origin 4.1
    git switch 4.1
    # Generate custom bindings
    ./your_godot_executable --dump-extension-api
    mv extension_api.json gdextension/extension_api.json
    ```

## Build project
From cppscript/
```bash
scons
```
or
```bash
scons build_library=false
```
after building library for your target once (saves couple of seconds)
## Recommended project layout
```
/                 project directory (res://)
├── bin           compiled binaries
├── cppscript     submodule 
└── src           C++ source files
 ```
## All working features
#### Example class in header (read comments)
```cpp
class Example : public Control {

	// Signals
	GSIGNAL(example_signal, float typed_arg, untyped_arg);

	// Group/subgroup
	GGROUP(Group);
	GSUBGROUP(Subgroup);

	// Property
	//
	// With custom getter/setter
	GPROPERTY(set_custom_position, get_custom_position);
	Vector2 custom_position;

public:	
	void set_custom_position(const Vector2 &pos);
	Vector2 get_custom_position() const;

private:

	// Without custom getter/setter
	// Generates set_float_auto/get_float_auto
	// public methods (also accessible in C++)
	GPROPERTY(set_float_auto, get_float_auto);
	float float_auto = 0;

	// With editor hint
	GPROPERTY(set_float_hint, get_float_hint,
		range, "0,1000,5");
	float float_hint = 0;

public:

	// Enum
	enum Constants {
		FIRST,
		ANSWER_TO_EVERYTHING = 42,
	};

	// Bitfield 
	GBITFIELD();
	enum Flags {
		FLAG_ONE = 1,
		FLAG_TWO = 2,
		FLAG_THREE = 4,
	};

	// Constants
	enum {
		CONSTANT_WITHOUT_ENUM = 314,
	};

	// Methods
	void simple_func();
	void simple_const_func() const;
	String image_ref_func(Ref<Image> p_image);
	String image_const_ref_func(const Ref<Image> &p_image);
	String return_something(const String &base);
	Viewport *return_something_const() const;

	// Ignore next public method/enum/constant declaration
	GIGNORE();
	int ignore_method();

    GIGNORE();
	enum ignore_enum {
        ONE,
        TWO,
    }

    GIGNORE();
	enum {
        IGNORE_CONSTANT = 42,
    }

	// Vararg method
	GVARARG(String named_arg, unnamed_arg);
	Variant varargs_func_example(const Variant **args, GDExtensionInt arg_count, GDExtensionCallError &error);

	// Default argument values
	int def_args(int p_a = 100, int p_b = 200);
    int def_args_string(String s = String("default"));  // Workaround for String 

	// RPC method 
	GRPC(authority, reliable, call_local);
	void rpc_example(int p_value);

	GRPC(any_peer, unreliable_ordered, call_remote, 42);
	void rpc_example2();

	// Static method
	static int test_static(int p_a, int p_b);
	
	// Register methods manually
	// (auto_methods = False)
	GMETHOD();
	Vector4 register_this() const;


	// Virtual methods
	virtual void virtual_example();

	// Methods starting with '_' are
	// used internally and don't need
	// to be registered
	virtual void _ready() override;
	virtual bool _has_point(const Vector2 &point) const override;
	virtual void _input(const Ref<InputEvent> &event) override;

	// Register your class
	// Possible class types:
	// basic class 		GCLASS(name, base_name)
	// virtual class 	GVIRTUAL_CLASS(name, base_name)
	// abstract class 	GABSTRACT_CLASS(name, base_name)
	GCLASS(Example, Control);
};
```
#### Generated code
```cpp
// Example : Control

void Example::_bind_methods() {
	ClassDB::bind_method(D_METHOD("set_custom_position", "pos"), &Example::set_custom_position);
	ClassDB::bind_method(D_METHOD("get_custom_position"), &Example::get_custom_position);
	ClassDB::bind_method(D_METHOD("simple_func"), &Example::simple_func);
	ClassDB::bind_method(D_METHOD("simple_const_func"), &Example::simple_const_func);
	ClassDB::bind_method(D_METHOD("image_ref_func", "p_image"), &Example::image_ref_func);
	ClassDB::bind_method(D_METHOD("image_const_ref_func", "p_image"), &Example::image_const_ref_func);
	ClassDB::bind_method(D_METHOD("return_something", "base"), &Example::return_something);
	ClassDB::bind_method(D_METHOD("return_something_const"), &Example::return_something_const);
	ClassDB::bind_method(D_METHOD("def_args", "p_a", "p_b"), &Example::def_args, DEFVAL(100), DEFVAL(200));
	ClassDB::bind_method(D_METHOD("def_args_string", "s"), &Example::def_args_string, DEFVAL(String("default")));
	ClassDB::bind_method(D_METHOD("rpc_example", "p_value"), &Example::rpc_example);
	ClassDB::bind_method(D_METHOD("rpc_example2"), &Example::rpc_example2);
	ClassDB::bind_method(D_METHOD("register_this"), &Example::register_this);
	ClassDB::bind_method(D_METHOD("get_float_auto"), &Example::get_float_auto);
	ClassDB::bind_method(D_METHOD("set_float_auto", "value"), &Example::set_float_auto);
	ClassDB::bind_method(D_METHOD("get_float_hint"), &Example::get_float_hint);
	ClassDB::bind_method(D_METHOD("set_float_hint", "value"), &Example::set_float_hint);


	ClassDB::bind_static_method("Example", D_METHOD("test_static", "p_a", "p_b"), &Example::test_static);


	BIND_VIRTUAL_METHOD(Example, virtual_example);


	{
	MethodInfo mi;
	mi.name = "varargs_func_example";
	mi.arguments.push_back(PropertyInfo(GetTypeInfo<String>::VARIANT_TYPE, "named_arg"));
	mi.arguments.push_back(PropertyInfo(GetTypeInfo<Variant>::VARIANT_TYPE, "unnamed_arg"));
	ClassDB::bind_vararg_method(METHOD_FLAGS_DEFAULT, "varargs_func_example", &Example::varargs_func_example, mi);
	}


	ADD_GROUP("Group", "group_");
	ADD_SUBGROUP("Subgroup", "group_subgroup_");
		ADD_PROPERTY(PropertyInfo(GetTypeInfo<decltype(custom_position)>::VARIANT_TYPE, "group_subgroup_custom_position", PROPERTY_HINT_NONE, ""), "set_custom_position", "get_custom_position");
		ADD_PROPERTY(PropertyInfo(GetTypeInfo<decltype(float_auto)>::VARIANT_TYPE, "group_subgroup_float_auto", PROPERTY_HINT_NONE, ""), "set_float_auto", "get_float_auto");
		ADD_PROPERTY(PropertyInfo(GetTypeInfo<decltype(float_hint)>::VARIANT_TYPE, "group_subgroup_float_hint", PROPERTY_HINT_RANGE, "0,1000,5"), "set_float_hint", "get_float_hint");


	ADD_SIGNAL(MethodInfo("example_signal", PropertyInfo(GetTypeInfo<float>::VARIANT_TYPE, "typed_arg"), PropertyInfo(GetTypeInfo<Variant>::VARIANT_TYPE, "untyped_arg")));


	BIND_ENUM_CONSTANT(FIRST);
	BIND_ENUM_CONSTANT(ANSWER_TO_EVERYTHING);


	BIND_BITFIELD_FLAG(FLAG_ONE);
	BIND_BITFIELD_FLAG(FLAG_TWO);
	BIND_BITFIELD_FLAG(FLAG_THREE);


	BIND_CONSTANT(CONSTANT_WITHOUT_ENUM);
}

// Call this in _ready() to configure RPC for your node
void Example::_rpc_config() {
	{
	Dictionary opts;
	opts["rpc_mode"] = MultiplayerAPI::RPC_MODE_AUTHORITY;
	opts["transfer_mode"] = MultiplayerPeer::TRANSFER_MODE_RELIABLE;
	opts["call_local"] = true;
	opts["channel"] = 0;
	rpc_config("rpc_example", opts);
	}
	{
	Dictionary opts;
	opts["rpc_mode"] = MultiplayerAPI::RPC_MODE_ANY_PEER;
	opts["transfer_mode"] = MultiplayerPeer::TRANSFER_MODE_UNRELIABLE_ORDERED;
	opts["call_local"] = false;
	opts["channel"] = 42;
	rpc_config("rpc_example2", opts);
	}
}

// Expands into setter/getter definitions
GENERATE_GETTER(Example::get_float_auto, Example::float_auto);
GENERATE_SETTER(Example::set_float_auto, Example::float_auto);
GENERATE_GETTER(Example::get_float_hint, Example::float_hint);
GENERATE_SETTER(Example::set_float_hint, Example::float_hint);

// godot-cpp macros to register enums/bitfields
// and be able to use them as method arguments
VARIANT_ENUM_CAST(Example::Constants);
VARIANT_BITFIELD_CAST(Example::Flags);
```
