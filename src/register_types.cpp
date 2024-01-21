#include <gdextension_interface.h>

#include <godot_cpp/core/class_db.hpp>
#include <godot_cpp/core/defs.hpp>
#include <godot_cpp/godot.hpp>

// Include custom headers here

#include "scripts.gen.h"
#include "register_types.h"

using namespace godot;

void initialize_scripts_module(ModuleInitializationLevel p_level) {
	switch (p_level) {
		case MODULE_INITIALIZATION_LEVEL_CORE:
			_register_level_core();
			break;
		case MODULE_INITIALIZATION_LEVEL_SERVERS:
			_register_level_servers();
			break;
		case MODULE_INITIALIZATION_LEVEL_SCENE:
			// Non-cppscript classes, static/global variables
			// initialization here

			_register_level_scene();
			break;
		case MODULE_INITIALIZATION_LEVEL_EDITOR:
			_register_level_editor();
			break;
		default:
			break;
	}
}

void uninitialize_scripts_module(ModuleInitializationLevel p_level) {
	switch (p_level) {
		case MODULE_INITIALIZATION_LEVEL_CORE:
			break;
		case MODULE_INITIALIZATION_LEVEL_SERVERS:
			break;
		case MODULE_INITIALIZATION_LEVEL_SCENE:
			// Non-cppscript classes, static/global variables
			// deinitialization here

			break;
		case MODULE_INITIALIZATION_LEVEL_EDITOR:
			break;
		default:
			break;
	}
}

extern "C" {
// GDExtension initialization
GDExtensionBool GDE_EXPORT scripts_library_init(GDExtensionInterfaceGetProcAddress p_get_proc_address, GDExtensionClassLibraryPtr p_library, GDExtensionInitialization *r_initialization) {
	godot::GDExtensionBinding::InitObject init_obj(p_get_proc_address, p_library, r_initialization);

	init_obj.register_initializer(initialize_scripts_module);
	init_obj.register_terminator(uninitialize_scripts_module);
	init_obj.set_minimum_library_initialization_level(DEFAULT_INIT_LEVEL);

	return init_obj.init();
}
}

