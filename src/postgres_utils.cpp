#include "postgres_utils.h"
#include <boost/algorithm/string/join.hpp>

// #include <spdlog/spdlog.h>

namespace util {
namespace postgres {

sql_select_identifier::sql_select_identifier(const std::string& identifier)
    : identifier(identifier) {
}

const sql_select_identifier sql_select_identifier::renamed_to(const std::string& new_name) const {
    return sql_select_identifier(identifier + " AS " + new_name);
}

const std::string sql_select_identifier::to_string() const {
    return identifier;
}

sql_column::sql_column(const std::string& name, const std::string& data_type, const sql_table* table)
    : name(name), data_type(data_type), table(table) {
}

const sql_select_identifier sql_column::get_sql_identifier() const {
    return sql_select_identifier(get_full_qualified_name());
}

sql_column_int::sql_column_int(const std::string& name, const sql_table* table)
    : sql_column(name, "int", table) {}

sql_column_float::sql_column_float(const std::string& name, const sql_table* table)
    : sql_column(name, "float", table) {}

sql_column_double::sql_column_double(const std::string& name, const sql_table* table)
    : sql_column(name, "double", table) {}

sql_column_text::sql_column_text(const std::string& name, const sql_table* table)
    : sql_column(name, "text", table) {}

sql_column_json::sql_column_json(const std::string& name, const sql_table* table)
    : sql_column(name, "json", table) {}

const sql_select_identifier sql_column_json::get_sql_identifier_as_text() const {
    return sql_select_identifier(get_full_qualified_name() + "::text");
}

sql_column_uuid::sql_column_uuid(const std::string& name, const sql_table* table)
    : sql_column(name, "uuid", table) {}

sql_column_postgis_point2d::sql_column_postgis_point2d(const std::string& name, const sql_table* table)
    : sql_column(name, "geometry(POINT)", table) {}

const sql_select_identifier sql_column_postgis_point2d::get_sql_identifier_x() const {
    return sql_select_identifier(std::string("ST_X(" + get_full_qualified_name() + std::string(")")));
}

const sql_select_identifier sql_column_postgis_point2d::get_sql_identifier_y() const {
    return sql_select_identifier(std::string("ST_Y(" + get_full_qualified_name() + std::string(")")));
}

sql_column_postgis_point3d::sql_column_postgis_point3d(const std::string& name, const sql_table* table)
    : sql_column(name, "geometry(POINTZ)", table) {}

const sql_select_identifier sql_column_postgis_point3d::get_sql_identifier_x() const {
    return sql_select_identifier(std::string("ST_X(" + get_full_qualified_name() + std::string(")")));
}

const sql_select_identifier sql_column_postgis_point3d::get_sql_identifier_y() const {
    return sql_select_identifier(std::string("ST_Y(" + get_full_qualified_name() + std::string(")")));
}

const sql_select_identifier sql_column_postgis_point3d::get_sql_identifier_z() const {
    return sql_select_identifier(std::string("ST_Z(" + get_full_qualified_name() + std::string(")")));
}

sql_column_timestamp::sql_column_timestamp(const std::string& name, const sql_table* table)
    : sql_column(name, "timestamp", table) {}

const sql_select_identifier sql_column_timestamp::get_sql_identifier_as_timestamp_float() const {
    const auto hours = std::string("date_part('hour', ") + get_full_qualified_name() + std::string(")");
    const auto minutes = std::string("date_part('minute', ") + get_full_qualified_name() + std::string(")");
    const auto seconds = std::string("date_part('second', ") + get_full_qualified_name() + std::string(")");
    return sql_select_identifier("60* (60* " + hours + " + " + minutes + ") + " + seconds + " AS timestamp_float");
}

bool sql_column::operator==(const sql_column& other) const {
    return name == other.name;
}

bool sql_column::operator<(const sql_column& other) const {
    return name < other.name;
}

bool sql_column::operator>(const sql_column& other) const {
    return name > other.name;
}

std::string sql_column::get_full_qualified_name() const {
    if (table) {
        return table->name + std::string(".") + name;
    }
    else {
        // spdlog::error("Table in sql_column {} is null! Returning column name only.", name);
        return name;
    }
}

sql_table::sql_table(const std::string& name)
    : schema("vslam"), name(name) {
}

void sql_table::register_pk(const std::shared_ptr<const sql_column>& primary_key) {
    this->primary_key = {primary_key->name, primary_key};
}

void sql_table::register_columns(const std::vector<std::shared_ptr<const sql_column>>& columns) {
    for (const auto& column : columns) {
        this->columns[column->name] = column;
    }
}

std::string sql_table::get_full_qualified_name() const {
    return schema.empty() ? name : schema + std::string(".") + name;
}

std::string sql_table::get_schema() const {
    return schema;
}

sql_camera_table::sql_camera_table(const sql_column_uuid& camera_id,
                                   const sql_column_text& camera_model,
                                   const sql_column_json& calibration,
                                   const sql_column_uuid& camera_rig_id)
    : sql_table("camera"), camera_id(camera_id), camera_model(camera_model), calibration(calibration), camera_rig_id(camera_rig_id) {
    register_pk(std::make_shared<const sql_column>(this->camera_id));
    register_columns({std::make_shared<const sql_column>(this->camera_model),
                      std::make_shared<const sql_column>(this->calibration),
                      std::make_shared<const sql_column>(this->camera_rig_id)});
}

sql_camera_table::sql_camera_table()
    : sql_camera_table(sql_column_uuid("camera_id", this),
                       sql_column_text("camera_model", this),
                       sql_column_json("calibration", this),
                       sql_column_uuid("c_rig_id_camera_rig", this)) {}

sql_landmark_table::sql_landmark_table(const sql_column_uuid& landmark_id,
                                       const sql_column_postgis_point3d& position,
                                       const sql_column_uuid& first_keyframe_id,
                                       const sql_column_uuid& reference_keyframe_id,
                                       const sql_column_int& num_observable,
                                       const sql_column_int& num_observed,
                                       const sql_column_uuid& map_id)
    : sql_table("landmark"), landmark_id(landmark_id), position(position), first_keyframe_id(first_keyframe_id),
      reference_keyframe_id(reference_keyframe_id), num_observable(num_observable), num_observed(num_observed), map_id(map_id) {
    register_pk(std::make_shared<const sql_column>(this->landmark_id));
    register_columns({std::make_shared<const sql_column>(this->position),
                      std::make_shared<const sql_column>(this->first_keyframe_id),
                      std::make_shared<const sql_column>(this->reference_keyframe_id),
                      std::make_shared<const sql_column>(this->num_observable),
                      std::make_shared<const sql_column>(this->num_observed),
                      std::make_shared<const sql_column>(this->map_id)});
}

sql_landmark_table::sql_landmark_table()
    : sql_landmark_table(sql_column_uuid("landmark_id", this),
                         sql_column_postgis_point3d("position", this),
                         sql_column_uuid("first_keyframe_id", this),
                         sql_column_uuid("reference_keyframe_id", this),
                         sql_column_int("num_observable", this),
                         sql_column_int("num_observed", this),
                         sql_column_uuid("map_id_map", this)) {}

sql_keypoint_table::sql_keypoint_table(const sql_column_uuid& keypoint_id,
                                       const sql_column_postgis_point2d& point,
                                       const sql_column_float& angle,
                                       const sql_column_int& octave,
                                       const sql_column_double& disparity,
                                       const sql_column_double& depth,
                                       const sql_column_uuid& landmark_id,
                                       const sql_column_uuid& keyframe_id,
                                       const sql_column_uuid& map_id)
    : sql_table("keypoint"), keypoint_id(keypoint_id), point(point), angle(angle), octave(octave), disparity(disparity),
      depth(depth), landmark_id(landmark_id), keyframe_id(keyframe_id), map_id(map_id) {
    register_pk(std::make_shared<const sql_column>(this->keypoint_id));
    register_columns({std::make_shared<const sql_column>(this->point),
                      std::make_shared<const sql_column>(this->angle),
                      std::make_shared<const sql_column>(this->octave),
                      std::make_shared<const sql_column>(this->disparity),
                      std::make_shared<const sql_column>(this->depth),
                      std::make_shared<const sql_column>(this->landmark_id),
                      std::make_shared<const sql_column>(this->keyframe_id),
                      std::make_shared<const sql_column>(this->map_id)});
}

sql_keypoint_table::sql_keypoint_table()
    : sql_keypoint_table(sql_column_uuid("kp_id", this),
                         sql_column_postgis_point2d("point", this),
                         sql_column_float("angle", this),
                         sql_column_int("octave", this),
                         sql_column_double("disparity", this),
                         sql_column_double("depth", this),
                         sql_column_uuid("landmark_id_landmark", this),
                         sql_column_uuid("keyframe_id_keyframe", this),
                         sql_column_uuid("map_id_map", this)) {}

sql_descriptor_table::sql_descriptor_table(const sql_column_uuid& descriptor_id,
                                           const sql_column_json& data,
                                           const sql_column_uuid& keypoint_id)
    : sql_table("descriptor"), descriptor_id(descriptor_id), data(data), keypoint_id(keypoint_id) {
    register_pk(std::make_shared<const sql_column>(this->descriptor_id));
    register_columns({std::make_shared<const sql_column>(this->data),
                      std::make_shared<const sql_column>(this->keypoint_id)});
}

sql_descriptor_table::sql_descriptor_table()
    : sql_descriptor_table(sql_column_uuid("d_id", this),
                           sql_column_json("data", this),
                           sql_column_uuid("kp_id_keypoint", this)) {}

sql_keyframe_table::sql_keyframe_table(const sql_column_uuid& keyframe_id,
                                       const sql_column_timestamp& timestamp,
                                       const sql_column_float& depth_threshold,
                                       const sql_column_json& rotation_cw,
                                       const sql_column_json& translation_cw,
                                       const sql_column_int& number_of_scale_levels,
                                       const sql_column_float& scale_factor,
                                       const sql_column_uuid& parent_id,
                                       const sql_column_uuid& source_frame_id,
                                       const sql_column_uuid& map_id,
                                       const sql_column_uuid& camera_rig_id)
    : sql_table("keyframe"), keyframe_id(keyframe_id), timestamp(timestamp), depth_threshold(depth_threshold),
      rotation_cw(rotation_cw), translation_cw(translation_cw), number_of_scale_levels(number_of_scale_levels),
      scale_factor(scale_factor), parent_id(parent_id), source_frame_id(source_frame_id), map_id(map_id), camera_rig_id(camera_rig_id) {
    register_pk(std::make_shared<const sql_column>(this->keyframe_id));
    register_columns({std::make_shared<const sql_column>(this->timestamp),
                      std::make_shared<const sql_column>(this->depth_threshold),
                      std::make_shared<const sql_column>(this->rotation_cw),
                      std::make_shared<const sql_column>(this->translation_cw),
                      std::make_shared<const sql_column>(this->number_of_scale_levels),
                      std::make_shared<const sql_column>(this->scale_factor),
                      std::make_shared<const sql_column>(this->parent_id),
                      std::make_shared<const sql_column>(this->source_frame_id),
                      std::make_shared<const sql_column>(this->map_id),
                      std::make_shared<const sql_column>(this->camera_rig_id)});
}

sql_keyframe_table::sql_keyframe_table()
    : sql_keyframe_table(sql_column_uuid("keyframe_id", this),
                         sql_column_timestamp("timestamp", this),
                         sql_column_float("depth_threshold", this),
                         sql_column_json("rotation_cw", this),
                         sql_column_json("translation_cw", this),
                         sql_column_int("number_of_scale_levels", this),
                         sql_column_float("scale_factor", this),
                         sql_column_uuid("parent_id", this),
                         sql_column_uuid("source_frame_id", this),
                         sql_column_uuid("map_id_map", this),
                         sql_column_uuid("c_rig_id_camera_rig", this)) {}

sql_map_table::sql_map_table(const sql_column_uuid& map_id,
                             const sql_column_text& name,
                             const sql_column_timestamp& valid_until)
    : sql_table("map"), map_id(map_id), name(name), valid_until(valid_until) {
    register_pk(std::make_shared<const sql_column>(this->map_id));
    register_columns({std::make_shared<const sql_column>(this->name),
                      std::make_shared<const sql_column>(this->valid_until)});
}

sql_map_table::sql_map_table()
    : sql_map_table(sql_column_uuid("map_id", this),
                    sql_column_text("name", this),
                    sql_column_timestamp("valid_until", this)) {}

sql_camera_rig_table::sql_camera_rig_table(const sql_column_uuid& camera_rig_id,
                                           const sql_column_text& name)
    : sql_table("camera_rig"), camera_rig_id(camera_rig_id), name(name) {
    register_pk(std::make_shared<const sql_column>(this->camera_rig_id));
    register_columns({std::make_shared<const sql_column>(this->name)});
}

sql_camera_rig_table::sql_camera_rig_table()
    : sql_camera_rig_table(sql_column_uuid("c_rig_id", this),
                           sql_column_text("name", this)) {}

sql_loop_edge_table::sql_loop_edge_table(const sql_column_uuid& loop_edge_table_pk,
                                         const sql_column_uuid& loop_edge_id,
                                         const sql_column_uuid& keyframe_id)
    : sql_table("loop_edge"), loop_edge_table_pk(loop_edge_table_pk), loop_edge_id(loop_edge_id), keyframe_id(keyframe_id) {
    register_pk(std::make_shared<const sql_column>(this->loop_edge_table_pk));
    register_columns({std::make_shared<const sql_column>(this->loop_edge_id),
                      std::make_shared<const sql_column>(this->keyframe_id)});
}

sql_loop_edge_table::sql_loop_edge_table()
    : sql_loop_edge_table(sql_column_uuid("loop_edge_table_pk", this),
                          sql_column_uuid("loop_edge_id", this),
                          sql_column_uuid("keyframe_id_keyframe", this)) {}

sql_child_keyframe_table::sql_child_keyframe_table(const sql_column_uuid& child_keyframe_table_pk,
                                                   const sql_column_uuid& child_keyframe_id,
                                                   const sql_column_uuid& keyframe_id)
    : sql_table("child_keyframe"), child_keyframe_table_pk(child_keyframe_table_pk), child_keyframe_id(child_keyframe_id), keyframe_id(keyframe_id) {
    register_pk(std::make_shared<const sql_column>(this->child_keyframe_table_pk));
    register_columns({std::make_shared<const sql_column>(this->child_keyframe_id),
                      std::make_shared<const sql_column>(this->keyframe_id)});
}

sql_child_keyframe_table::sql_child_keyframe_table()
    : sql_child_keyframe_table(sql_column_uuid("child_keyframe_table_pk", this),
                               sql_column_uuid("child_keyframe_id", this),
                               sql_column_uuid("keyframe_id_keyframe", this)) {}

std::string create_insert(const sql_table& table, const std::map<const sql_column, std::string>& key_value_pairs) {
    if (key_value_pairs.empty()) {
        // spdlog::error("No key/value pairs given to insert into table '{}'! Returning empty string...", table.name);
        return "";
    }

    std::vector<std::string> keys;
    std::vector<std::string> values;
    for (const auto& key_value : key_value_pairs) {
        keys.push_back(key_value.first.name);
        values.push_back(key_value.second);
    }

    const std::string INSERT_INTO = "INSERT INTO " + table.get_full_qualified_name();
    const std::string KEY_STRING = "(" + boost::algorithm::join(keys, ", ") + ")";
    const std::string VALUE_STRING = "(" + boost::algorithm::join(values, ", ") + ")";

    return INSERT_INTO + " " + KEY_STRING + " VALUES " + VALUE_STRING + ";";
}


std::string create_select(const std::vector<sql_select_identifier>& cols,
                              bool distinct,
                              const sql_table& from,
                              const std::vector<std::pair<const sql_table, std::pair<const sql_column, const sql_column>>>& join_on,
                              const std::string& where_clause) {
    if (cols.empty()) {
        // spdlog::error("No rows to select! Returning empty string...");
        return "";
    }

    const std::string SELECT = std::string("SELECT") + (distinct ? std::string(" DISTINCT") : std::string(""));
    std::vector<std::string> cols_strings;
    for (const auto& col : cols) {
        cols_strings.emplace_back(col.to_string());
    }
    const std::string COLS = boost::algorithm::join(cols_strings, ", ");

    std::string ret_sql_string = SELECT + std::string(" ") + COLS + std::string(" ");
    ret_sql_string += std::string("FROM ") + from.get_full_qualified_name() + std::string(" ");

    for (const auto& join_on_pair : join_on) {
        ret_sql_string += (std::string("JOIN ") + join_on_pair.first.get_full_qualified_name() + std::string(" "));
        ret_sql_string += (std::string("ON (") + join_on_pair.second.first.get_full_qualified_name() + std::string(" = ") + join_on_pair.second.second.get_full_qualified_name() + std::string(") "));
    }

    return ret_sql_string + (where_clause.empty() ? std::string("") : (std::string(" WHERE ") + where_clause)) + std::string(";");
}

std::string add_single_quotes(const std::string& input) {
    return "'" + input + "'";
}

std::string get_postgis_point(double x, double y) {
    return "ST_GeomFromText('POINT (" + std::to_string(x) + " " + std::to_string(y) + ")')";
}

std::string get_postgis_point(double x, double y, double z) {
    return "ST_GeomFromText('POINT Z (" + std::to_string(x) + " " + std::to_string(y) + " " + std::to_string(z) + ")')";
}

} // namespace postgres
} // namespace util
