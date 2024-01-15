// Template file to use with godot-cppscript
#ifndef REGISTER_TYPES_H
#define REGISTER_TYPES_H

#include <godot_cpp/core/class_db.hpp>

using namespace godot;

void initialize_scripts_module(ModuleInitializationLevel p_level);
void uninitialize_scripts_module(ModuleInitializationLevel p_level);

#endif // REGISTER_TYPES_H
