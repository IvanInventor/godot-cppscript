**[Documentation](https://github.com/IvanInventor/godot-cppscript/wiki) | [Usage example](#usage-example)**

# godot-cpp-script

Python script that uses various C++ macros and templates to automate binding code generation and provide short and readable godot-specific compile error messages. With simple configuration, can attach to existing SCons/CMake build tool. Works similar to [Unreal Header Tool](https://docs.unrealengine.com/5.3/en-US/unreal-header-tool-for-unreal-engine/).

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

# Installation

### From zero
Install template from [here](https://github.com/IvanInventor/godot-cppscript-template).

##
### To existing project
Copy `godot_cppscript.*` to your project
- `godot_cppscript.py` for SCons

    ***OR***
  
- `godot_cppscript.cmake` for CMake

    ***OR***
  
- Setup git submodule from root of your project

  Recommended project layout
  ```
  /                   project root
  ├── project 	    godot project root (res://)
  ├── bin             compiled binaries
  ├── external        submodules
  │   ├── cppscript
  │   └── godot-cpp
  ├── src             C++ source files
  └── include         (optional) separated header files
   ```

  ```bash
  $ git submodule add https://github.com/IvanInventor/godot-cppscript external/cppscript
  $ git submodule update --init external/cppscript
  ```
##### Generate files
Once per project, need to copy/modify some files (library_name = 'scripts', for example)
  - `.gdextension` file
  - `register_types.cpp`
  - `register_types.h`

Don't worry, you will still be able to add custom code to this files after configuring

- By script
    - With Python
    ```bash
    # Usage:
    # python3 path/to/godot_cppscript.py
    # <library_name>              (`my_library_name`)
    # <cpp_file_path>             (`src/register_types.cpp`)
    # <header_file_path>          (`include/register_types.h`)
    # <gdextension_file_path>     (`project/my_library.gdextension`)
    $ python3 godot_cppscript.py scripts src/register_types.cpp src/register_types.h project/scripts.gdextension
    These files will be affected:
        (Override) project/scripts.gdextension
        (Override) src/register_types.cpp
        (Override) src/register_types.h

    Are you sure? (Y/N) Y
    Configuring 'project/scripts.gdextension' ...
    Configuring 'src/register_types.cpp' ...
    Configuring 'src/register_types.h' ...
    Files configured.
    ```
        
    ***OR***
  
  - With cmake
    ```bash
    # Usage:
    # cmake -P path/to/godot_cppscript.cmake
    # <library_name>              (`my_library_name`)
    # <cpp_file_path>             (`src/register_types.cpp`)
    # <header_file_path>          (`include/register_types.h`)
    # <gdextension_file_path>     (`project/my_library.gdextension`)
    $ cmake -P godot_cppscript.cmake scripts src/register_types.cpp src/register_types.h project/scripts.gdextension
    These files will be affected:
        (Override) project/scripts.gdextension
        (Override) src/register_types.cpp
        (Override) src/register_types.h

    Are you sure? (Y/N) Y
    Configuring 'project/scripts.gdextension' ...
    Configuring 'src/register_types.cpp' ...
    Configuring 'src/register_types.h' ...
    Files configured.
    ```

    ***OR***
  
  - By hand, replacing `@LIBRARY_NAME@` in files with you library name
    - [templates/scripts.gdextension.in](https://github.com/IvanInventor/godot-cppscript/blob/next/templates/scripts.gdextension.in) -> project/<library_name>.gdextension
    - [templates/register_types.cpp.in](https://github.com/IvanInventor/godot-cppscript/blob/next/templates/register_types.cpp.in) -> src/register_types.cpp
    - [templates/register_types.h.in](https://github.com/IvanInventor/godot-cppscript/blob/next/templates/register_types.h.in) -> src/register_types.h

- Create cppscript target in your build script
  - SCons
  ```python
  from godot_cppscript import create_cppscript_target
  import glob

  # ...

  # Get list of headers (Prefer *.hpp files)
  scripts = glob.glob('src/**/*.hpp', recursive=True)

  # Create target, returns generated .cpp files list
  generated = create_cppscript_target(
  		env,		# SCons env, env.Clone() for different projects
  		scripts,	# Header files to parse
  
  		# CppScript config
  		{
  		# Name of header to be included to enable cppscript
  		# (Prefer name unique to your project)
  		'header_name' : 'cppscript.h',
  
  		# Path to C++ header files
  		'header_dir' : 'src',
  
  		# Path to generated object files
  		'gen_dir' : ".gen",
  
  		# Generate bindings to public methods automatically
  		# or require GMETHOD() before methods
  		'auto_methods' : True,
  
  		# Optional
  
  		## C++ defines (TOOLS_ENABLED, DEBUG_METHODS etc.)
  		## Enable, if you conditionally enable classes/members
  		## based on definitions
  		'compile_defs' : env['CPPDEFINES'],
  		#
  		## Include paths
  		## (Try to avoid godot-cpp headers paths,
  		## it slows parsing drastically)
  		#'include_paths' : env['CPPPATH']
  		}
  )
  
  # Include headers path (if not done already)
  env.Append(CPPPATH='src')

  # Your project's target generation
  # You only need to modify it
  if env["platform"] == "macos":
      library = env.SharedLibrary(
  	"bin/lib{}.{}.{}.framework/lib{}.{}.{}".format(
  	library_name, env["platform"], env["target"], library_name, env["platform"], env["target"]
  	),
  	# source=sources
  	source=sources + generated, # Add generated source files to target
      )
  else:
      library = env.SharedLibrary(
  	"bin/lib{}{}{}".format(library_name, env["suffix"], env["SHLIBSUFFIX"]),
  	# source=sources
  	source=sources + generated, # Add generated source files to target
      )
  
  # Rebuild after headers change
  env.Depends(library[0].sources, generated)
  ```
  
  - Cmake
  ```cmake
  include(${CMAKE_CURRENT_SOURCE_DIR}/godot_cppscript.cmake)
  
  # Get header files (Prefer .hpp files)
  file(GLOB_RECURSE CPPSCRIPT_HEADERS src/*.hpp)
  
  # Call function to create cppscript target
  create_cppscript_target(
  	# Name of header to be included to enable cppscript
  	# (Prefer name unique to your project)
  	HEADER_NAME
  		cppscript.h
  
  	# Header files to parse (.hpp only)
  	HEADERS_LIST
  		${CPPSCRIPT_HEADERS}
  
  	# FULL PATH to C++ header files
  	HEADERS_DIR
  		${CMAKE_CURRENT_SOURCE_DIR}/src
  	
  	# Variable name for generated sources list
  	OUTPUT_SOURCES
  		GEN_SOURCES
  
  	# Generate bindings to public methods automatically
  	# or require GMETHOD() before methods
  	AUTO_METHODS
  
  	# Optional
  
  	# C++ defines (TOOLS_ENABLED, DEBUG_METHODS etc.)
  	# Enable, if you conditionally enable classes/members
  	# based on definitions
  	#
  	 COMPILE_DEFS
  	 	$<TARGET_PROPERTY:${PROJECT_NAME},COMPILE_DEFINITIONS>
  
  	# Include paths
  	# (Try to avoid godot-cpp headers paths,
  	# it slows parsing drastically)
  	#
  	# INCLUDE_PATHS
  	# 	$<TARGET_PROPERTY:${PROJECT_NAME},INCLUDE_DIRECTORIES>
  )
  
  # Add sources to your target
  target_sources(${PROJECT_NAME} PRIVATE ${GEN_SOURCES})
  
  # Include headers path (if not done already)
  target_include_directories(${PROJECT_NAME} PRIVATE
  	src
  )
  ```

## Usage example

#### Header syntax (read comments)
```cpp
#include <godot_cpp/classes/control.hpp>
#include <godot_cpp/classes/image.hpp>
#include <godot_cpp/classes/input_event_key.hpp>
#include <godot_cpp/classes/tile_map.hpp>
#include <godot_cpp/classes/tile_set.hpp>
#include <godot_cpp/classes/viewport.hpp>

// Include cppscript header (prefer custom name)
#include <cppscript.h>

using namespace godot;

class ExampleForRepo : public Control {
	// Register your class
	// Possible class types:
	// basic class 		GCLASS(name, base_name)
	// virtual class 	GVIRTUAL_CLASS(name, base_name)
	// abstract class 	GABSTRACT_CLASS(name, base_name)
	GCLASS(ExampleForRepo, Control);

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
    	};

    	GIGNORE();
	enum {
        	IGNORE_CONSTANT = 42,
    	};

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

	// Virtual methods starting with '_' are
	// used internally and don't need
	// to be registered
	void _ready() override;
	bool _has_point(const Vector2 &point) const override;
	void _input(const Ref<InputEvent> &event) override;

};

```
#### Generated code
```cpp
/*-- GENERATED FILE - DO NOT EDIT --*/

#include <cppscript_bindings.h>

#include "../src/example_for_repo.hpp"

using namespace godot;

// ExampleForRepo : Control

void ExampleForRepo::_bind_methods() {
	Method<&ExampleForRepo::set_custom_position>::bind(D_METHOD("set_custom_position", "pos"));
	Method<&ExampleForRepo::get_custom_position>::bind(D_METHOD("get_custom_position"));
	Method<&ExampleForRepo::simple_func>::bind(D_METHOD("simple_func"));
	Method<&ExampleForRepo::simple_const_func>::bind(D_METHOD("simple_const_func"));
	Method<&ExampleForRepo::image_ref_func>::bind(D_METHOD("image_ref_func", "p_image"));
	Method<&ExampleForRepo::image_const_ref_func>::bind(D_METHOD("image_const_ref_func", "p_image"));
	Method<&ExampleForRepo::return_something>::bind(D_METHOD("return_something", "base"));
	Method<&ExampleForRepo::return_something_const>::bind(D_METHOD("return_something_const"));
	Method<&ExampleForRepo::def_args>::bind(D_METHOD("def_args", "p_a", "p_b"), DEFVAL(100), DEFVAL(200));
	Method<&ExampleForRepo::def_args_string>::bind(D_METHOD("def_args_string", "s"), DEFVAL(String("default")));
	Method<&ExampleForRepo::rpc_example>::bind(D_METHOD("rpc_example", "p_value"));
	Method<&ExampleForRepo::rpc_example2>::bind(D_METHOD("rpc_example2"));
	Method<&ExampleForRepo::register_this>::bind(D_METHOD("register_this"));
	Method<&ExampleForRepo::virtual_example>::bind(D_METHOD("virtual_example"));
	Method<&ExampleForRepo::get_float_auto>::bind(D_METHOD("get_float_auto"));
	Method<&ExampleForRepo::set_float_auto>::bind(D_METHOD("set_float_auto", "value"));
	Method<&ExampleForRepo::get_float_hint>::bind(D_METHOD("get_float_hint"));
	Method<&ExampleForRepo::set_float_hint>::bind(D_METHOD("set_float_hint", "value"));


	StaticMethod<&ExampleForRepo::test_static>::bind(get_class_static(), D_METHOD("test_static", "p_a", "p_b"));


	Method<&ExampleForRepo::varargs_func_example>::bind_vararg("varargs_func_example"
		,MakePropertyInfo<String>("named_arg")
		,MakePropertyInfo<Variant>("unnamed_arg")
		);


	ADD_GROUP("Group", "group_");
	ADD_SUBGROUP("Subgroup", "group_subgroup_");
		ADD_PROPERTY(MakePropertyInfo<decltype(custom_position)>("group_subgroup_custom_position"), "set_custom_position", "get_custom_position");
		ADD_PROPERTY(MakePropertyInfo<decltype(float_auto)>("group_subgroup_float_auto"), "set_float_auto", "get_float_auto");
		ADD_PROPERTY(MakePropertyInfo<decltype(float_hint)>("group_subgroup_float_hint", PROPERTY_HINT_RANGE, "0,1000,5"), "set_float_hint", "get_float_hint");


	ADD_SIGNAL(MethodInfo("example_signal"
		,MakePropertyInfo<float>("typed_arg")
		,MakePropertyInfo<Variant>("untyped_arg")
		));


	BIND_ENUM_CONSTANT(FIRST);
	BIND_ENUM_CONSTANT(ANSWER_TO_EVERYTHING);


	BIND_BITFIELD_FLAG(FLAG_ONE);
	BIND_BITFIELD_FLAG(FLAG_TWO);
	BIND_BITFIELD_FLAG(FLAG_THREE);


	BIND_CONSTANT(CONSTANT_WITHOUT_ENUM);
}

void ExampleForRepo::_rpc_config() {
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

GENERATE_GETTER(ExampleForRepo::get_float_auto, ExampleForRepo::float_auto);
GENERATE_SETTER(ExampleForRepo::set_float_auto, ExampleForRepo::float_auto);
GENERATE_GETTER(ExampleForRepo::get_float_hint, ExampleForRepo::float_hint);
GENERATE_SETTER(ExampleForRepo::set_float_hint, ExampleForRepo::float_hint);

VARIANT_ENUM_CAST(ExampleForRepo::Constants);
VARIANT_BITFIELD_CAST(ExampleForRepo::Flags);

```




