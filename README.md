# godot-cpp-script

Python script that implements various C++ macros to automate binding code generation. Used as SCons custom builder besides default library builder. Works similar to [Unreal Header Tool](https://docs.unrealengine.com/5.3/en-US/unreal-header-tool-for-unreal-engine/).

[Example project](https://github.com/IvanInventor/godot-cppscript-example)

[Keywords description](https://github.com/IvanInventor/godot-cppscript-example/blob/master/src/example.hpp) (read comments)

[Property hints description](https://github.com/IvanInventor/godot-cppscript-example/blob/master/src/example_properties.hpp) (read comments)
## Dependencies
#### Programs
[Godot 4](https://godotengine.org/download/archive/) (>4.1)

[Python](https://www.python.org/downloads/)

[SCons](https://scons.org/pages/download.html)




#### Python dependencies
libclang, pcpp
```bash
pip install libclang pcpp
```
## Installation

### As project submodule

- From root of your project (git initialized)
```bash
git submodule add https://github.com/IvanInventor/godot-cpp-script cppscript
git submodule update --recursive --init cppscript
```
- Checkout your [version](https://github.com/godotengine/godot-cpp/tags) of godot
```bash
cd cppscript/godot-cpp/
git checkout <tag>
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



