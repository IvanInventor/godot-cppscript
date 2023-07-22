#include "macros.h"

namespace ClassDB {
	template<class T>
		void register_class() {};

	template<class ...Args>
		void bind_method(Args ...args) {};
}
class def {};
class MyClass : def {
	EXPORT_CLASS(MyClass);
	
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
	EXPORT_CLASS(Myclass123);

	EXPORT_METHOD()
	int my1() {
		return 123;
	}

EXPORT_METHOD(gg_h, Default(123))
void gg_h() { };

};
