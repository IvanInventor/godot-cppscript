# godot-cpp-script

Python script on top of SCons file to generate binding code for godot-cpp.

## Usage

1. Clone repository
2. Create root directory for your project with any name
3. Add scripts.gdextension to project root


Compile with
```bash
scons
```
Or
```bash
scons build_library=false
```
if you've built library once for faster compilation
## Example
Check example yourself on example branch

Class definition with new syntax
```cpp
class MySprite : public Sprite2D {
	GCLASS(MySprite, Sprite2D);

public:
	
	enum named_enum {
		ONE = 1,
		TWO,
		THREE,
	};

	enum {
		UNNAMED_ONE = 1,
		UNNAMED_TWO,
		UNNAMED_THREE,
	};
	
	GGROUP(Main group);
	GSUBGROUP(Submain group)

	GPROPERTY(set_speed, get_speed);
	GEXPORT_RANGE(0,360,0.1);
	float speed = 0.0;
	void set_speed(float speed);
	float get_speed();

	GGROUP(Enums);

	GPROPERTY(set_enumtest, get_enumtest);
	GEXPORT_ENUM(A,B,C);
	int enumtest = 0;
	void set_enumtest(int enumtest);
	int get_enumtest();

	GGROUP(Flags);

	GPROPERTY(set_rendertest, get_rendertest);
	GEXPORT_LAYERS_2D_RENDER();
	int rendertest;
	void set_rendertest(int flags);
	int get_rendertest();

	void _process(float);

	void reset_rotation();

	static void static_method();

};
```
Generated bindings
```cpp
inline void register_script_classes() {
	ClassDB::register_class<MySprite>();
}
void MySprite::_bind_methods() {
	ADD_GROUP("Enums", "enums_");
	ADD_GROUP("Flags", "flags_");
	ADD_GROUP("Main group", "maingroup_");
	ADD_SUBGROUP("Submain group", "maingroup_submaingroup_");
	ClassDB::bind_method(D_METHOD("set_speed", "speed"), &MySprite::set_speed);
	ClassDB::bind_method(D_METHOD("get_speed"), &MySprite::get_speed);
	ClassDB::bind_method(D_METHOD("set_enumtest", "enumtest"), &MySprite::set_enumtest);
	ClassDB::bind_method(D_METHOD("get_enumtest"), &MySprite::get_enumtest);
	ClassDB::bind_method(D_METHOD("set_rendertest", "flags"), &MySprite::set_rendertest);
	ClassDB::bind_method(D_METHOD("get_rendertest"), &MySprite::get_rendertest);
	ClassDB::bind_method(D_METHOD("reset_rotation"), &MySprite::reset_rotation);
	ClassDB::bind_static_method("MySprite", D_METHOD("static_method"), &MySprite::static_method);
	ADD_PROPERTY(PropertyInfo(GetTypeInfo<float>::VARIANT_TYPE, "maingroup_submaingroup_speed", PROPERTY_HINT_RANGE, "0,360,0.1"), "set_speed", "get_speed");
	ADD_PROPERTY(PropertyInfo(GetTypeInfo<int>::VARIANT_TYPE, "enums_enumtest", PROPERTY_HINT_ENUM, "A,B,C"), "set_enumtest", "get_enumtest");
	ADD_PROPERTY(PropertyInfo(GetTypeInfo<int>::VARIANT_TYPE, "flags_rendertest", PROPERTY_HINT_LAYERS_2D_RENDER, ""), "set_rendertest", "get_rendertest");
	BIND_ENUM_CONSTANT(ONE);
	BIND_ENUM_CONSTANT(TWO);
	BIND_ENUM_CONSTANT(THREE);
	BIND_CONSTANT(UNNAMED_ONE);
	BIND_CONSTANT(UNNAMED_TWO);
	BIND_CONSTANT(UNNAMED_THREE);
};
VARIANT_ENUM_CAST(MySprite::named_enum);

```
## List of all working features

- [x] Register class
- [ ] Register abstract class
- [ ]	Generate _bind_methods:
    - [x] Simple bind
    - [x] With args decsription
    - [ ] With DEFVAL
    - [x] Static methods
    -  [ ] With varargs
- [x] Properties
- [x] Group/subgroup of properties
- [ ] Signals
- [x] Constants
- [x] Enums:
    - [ ] Outside of class
- [ ] Bitfields
- [ ] Constants w/o class
- [ ] Enums w/o class
-  [ ] RPCs
