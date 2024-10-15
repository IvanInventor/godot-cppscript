/* CppScript example of property hints
 *
 * All hints with available documentation are used here
 */
#include <godot_cpp/classes/control.hpp>
#include <godot_cpp/classes/expression.hpp>
#include <godot_cpp/classes/texture2d.hpp>
#include <godot_cpp/variant/quaternion.hpp>

#include <cppscript.h>

using namespace godot;

class ExampleProperties : public Control {
	GCLASS(ExampleProperties, Control);

public:
	GGROUP(Basic types);

	GSUBGROUP(int);

	// Arguments of GPROPERTY:
	// setter	- custom or auto generated
	// getter	- custom or auto generated
	// hint_type
	// hint_string
	//
	// hint_type - name of type from
	// PropertyHint enum without PROPERTY_HINT part,
	// optionally lowercase
	//
	// PROPERTY_HINT_RANGE -> range
	// PROPERTY_HINT_LAYERS_2D_RENDER -> layers_2d_render
	//
	// hint_string - C-style string,
	// content depends on hint type
	// can be omitted in GPROPERTY()
	//
	// See: PropertyHint enum in editor
	// documentation for all hint types

	GPROPERTY(set_nohint, get_nohint,
		none);
	int nohint_property = 0;

	GPROPERTY(set_enum, get_enum,
		enum, "Select:2,Any:4,Word:6");
	int enum_property = 2;

	GPROPERTY(set_object_id, get_object_id,
		object_id);
	int object_id_property = 0;




	GSUBGROUP(float);

	GPROPERTY(set_range, get_range,
		range, "0,100,0.1");
	float range_property = 0;

	GPROPERTY(set_easing, get_easing,
		exp_easing, "positive_only");
	float easing_property = 0;




	GSUBGROUP(String);

	GPROPERTY(set_suggestion, get_suggestion,
		enum_suggestion, "Suggest,this,strings");
	String suggestion_property;

	GPROPERTY(set_multiline, get_multiline,
		multiline_text);
	String multiline_property;

	GPROPERTY(set_password, get_password,
		password);
	String password_property;

	GPROPERTY(set_expression, get_expression,
		expression, "");
	String expression_property;

	GPROPERTY(set_placeholder, get_placeholder,
		placeholder_text, "Placeholder...");
	String placeholder_property;

	GPROPERTY(set_type_string, get_type_string,
		type_string, "Control");
	String type_string_property;

	GPROPERTY(set_node_type, get_node_type,
		node_type, "Control");
	String node_type_property;



	GGROUP(Vector);

	GPROPERTY(set_link, get_link,
		link);
	Vector2 link_property{5, 10};




	GGROUP(Flags);

	GPROPERTY(set_flags, get_flags,
		flags, "One,Two,Three,Five:16");
	int flags_property = 0;

	GPROPERTY(set_2d_render, get_2d_render,
		layers_2d_render);
	int property_2d_render = 0;

	GPROPERTY(set_2d_physics, get_2d_physics,
		layers_2d_physics);
	int property_2d_physics = 0;

	GPROPERTY(set_2d_navigation, get_2d_navigation,
		layers_2d_navigation);
	int property_2d_navigation = 0;

	GPROPERTY(set_3d_render, get_3d_render,
		layers_3d_render);
	int property_3d_render = 0;

	GPROPERTY(set_3d_physics, get_3d_physics,
		layers_3d_physics);
	int property_3d_physics = 0;

	GPROPERTY(set_3d_navigation, get_3d_navigation,
		layers_3d_navigation);
	int property_3d_navigation = 0;




	GGROUP(Color);

	GPROPERTY(set_color_noalpha, get_color_noalpha,
		color_no_alpha);
	Color color_noalpha_property;




	GGROUP(Files);

	GPROPERTY(set_file, get_file,
		file, "*.gd");
	String file_property;

	GPROPERTY(set_dir, get_dir,
		dir);
	String dir_property;

	GPROPERTY(set_global_file, get_global_file,
		global_file, "*.png");
	String global_file_property;

	GPROPERTY(set_global_dir, get_global_dir,
		global_dir);
	String global_dir_property;




	GGROUP(Localization);

	GPROPERTY(set_locale_id, get_locale_id,
		locale_id);
	String locale_id_property;

	GPROPERTY(set_localizable_string, get_localizable_string,
		localizable_string, "");
	Dictionary localizable_string_property;




	GGROUP(Resource);

	GPROPERTY(set_resource_type, get_resource_type,
		resource_type, "Texture2D,AtlasTexture");
	Ref<Texture2D> resource_type_property;




	GGROUP(Others);

	GPROPERTY(set_hide_quat_edit, get_hide_quat_edit,
		hide_quaternion_edit);
	Quaternion hide_quat_edit_property;

	/* No documentation
	 *
	GPROPERTY(set_node_path_to_edited_node, get_node_path_to_edited_node,
		node_path_to_edited_node);
	NodePath node_path_to_edited_node_property;

	GPROPERTY(set_object_too_big, get_object_too_big,
		object_too_big);
	Object object_too_big_property;

	GPROPERTY(set_node_path_valid_types, get_node_path_valid_types,
		node_path_valid_types, "Control");
	NodePath node_path_valid_types_property;

	GPROPERTY(set_save_file, get_save_file,
		save_file);
	String save_file_property;

	GPROPERTY(set_global_save_file, get_global_save_file,
		global_save_file);
	String global_save_file_property;

	GPROPERTY(set_int_is_objectid, get_int_is_objectid,
		int_is_objectid);
	int int_is_objectid_property = 0;

	GPROPERTY(set_int_is_pointer, get_int_is_pointer,
		int_is_pointer);
	int int_is_pointer_property = 0;

	GPROPERTY(set_array_type, get_array_type,
		array_type);
	Array array_type_property;
	*/
};
