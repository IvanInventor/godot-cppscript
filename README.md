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
## List of all working features
- [x] Register class (basic, abstract, virtual)
- [x] Signals
- [x] Methods
    - [x] With default arguments value
    - [x] Static methods
    - [x] With varargs
    - [x] RPC
- [x] Properties
    - [x] Auto-generated setter/getter
    - [x] Property hints
    - [x] Group/subgroup
- [x] Constants
- [x] Enums
- [x] Bitfields



