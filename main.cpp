#include "macros.h"

#include <godot_cpp/classes/sprite2d.hpp>

using namespace godot;
class MyClass : public Sprite2D {
	GCLASS(MyClass, Sprite2D);
	
public: 
	EXPORT_METHOD(my_method(123))
	int  my_method(int a, int b) {
		return 123;
	}
	EXPORT_METHOD(my_method2, my_method2(123, 456))
	int my_method2() {
		return 123;
	}
};

