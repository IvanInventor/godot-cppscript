#include "macros.h"

class def {};
class MyClass : def {
	EXPORT_CLASS(MyClass, def);
	
	EXPORT_METHOD(my_method(123))
	int my_method() {
		return 123;
	}
	EXPORT_METHOD(my_method2, my_method2(123, 456))
	int my_method2() {
		return 123;
	}
};


class Myclass123 {
	EXPORT_CLASS(MyClass123, Button);

	EXPORT_METHOD()
	int my1() {
		return 123;
	}
};

EXPORT_METHOD(My_class, Default(123))
Ref<int> gg-h() { }
