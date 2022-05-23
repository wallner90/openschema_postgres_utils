#pragma once

#include <string>
#include <vector>
#include <map>
#include <memory>

namespace util {
namespace postgres {

class sql_table;
class sql_column;

class sql_select_identifier {
public:
    sql_select_identifier(const std::string& identifier);
    const sql_select_identifier renamed_to(const std::string& new_name) const;
    const std::string to_string() const;

    std::string identifier;
};

class sql_column {
public:
    sql_column(const std::string& name, const std::string& data_type, const sql_table* table);
    std::string get_full_qualified_name() const;
    const sql_select_identifier get_sql_identifier() const;

    const std::string name;
    const std::string data_type;
    const sql_table* table;

    // needed to use as map key
    bool operator==(const sql_column& other) const;
    bool operator<(const sql_column& other) const;
    bool operator>(const sql_column& other) const;

protected:
};

class sql_column_int : public sql_column {
public:
    sql_column_int(const std::string& name, const sql_table* table);
};

class sql_column_float : public sql_column {
public:
    sql_column_float(const std::string& name, const sql_table* table);
};

class sql_column_double : public sql_column {
public:
    sql_column_double(const std::string& name, const sql_table* table);
};

class sql_column_text : public sql_column {
public:
    sql_column_text(const std::string& name, const sql_table* table);
};

class sql_column_json : public sql_column {
public:
    sql_column_json(const std::string& name, const sql_table* table);
    const sql_select_identifier get_sql_identifier_as_text() const;
};

class sql_column_uuid : public sql_column {
public:
    sql_column_uuid(const std::string& name, const sql_table* table);
};

class sql_column_postgis_point2d : public sql_column {
public:
    sql_column_postgis_point2d(const std::string& name, const sql_table* table);
    const sql_select_identifier get_sql_identifier_x() const;
    const sql_select_identifier get_sql_identifier_y() const;
};

class sql_column_postgis_point3d : public sql_column {
public:
    sql_column_postgis_point3d(const std::string& name, const sql_table* table);
    const sql_select_identifier get_sql_identifier_x() const;
    const sql_select_identifier get_sql_identifier_y() const;
    const sql_select_identifier get_sql_identifier_z() const;
};

class sql_column_timestamp : public sql_column {
public:
    sql_column_timestamp(const std::string& name, const sql_table* table);
    const sql_select_identifier get_sql_identifier_as_timestamp_float() const;
};

class sql_table {
public:
    sql_table(const std::string& name);

    void register_pk(const std::shared_ptr<const sql_column>& primary_key);
    void register_columns(const std::vector<std::shared_ptr<const sql_column>>& columns);

    std::string get_full_qualified_name() const;
    std::string get_schema() const;

    const std::string schema;
    const std::string name;
    std::pair<std::string, std::shared_ptr<const sql_column>> primary_key;
    std::map<std::string, std::shared_ptr<const sql_column>> columns;

protected:
};

class sql_camera_table : public sql_table {
public:
    sql_camera_table();
    sql_camera_table(const sql_column_uuid& camera_id,
                     const sql_column_text& camera_model,
                     const sql_column_json& calibration,
                     const sql_column_uuid& camera_rig_id);

    const sql_column_uuid camera_id;
    const sql_column_text camera_model;
    const sql_column_json calibration;
    const sql_column_uuid camera_rig_id;

protected:
};

class sql_landmark_table : public sql_table {
public:
    sql_landmark_table();
    sql_landmark_table(const sql_column_uuid& landmark_id,
                       const sql_column_postgis_point3d& position,
                       const sql_column_uuid& first_keyframe_id,
                       const sql_column_uuid& reference_keyframe_id,
                       const sql_column_int& num_observable,
                       const sql_column_int& num_observed,
                       const sql_column_uuid& map_id);

    const sql_column_uuid landmark_id;
    const sql_column_postgis_point3d position;
    const sql_column_uuid first_keyframe_id;
    const sql_column_uuid reference_keyframe_id;
    const sql_column_int num_observable;
    const sql_column_int num_observed;
    const sql_column_uuid map_id;

protected:
};

class sql_keypoint_table : public sql_table {
public:
    sql_keypoint_table();
    sql_keypoint_table(const sql_column_uuid& keypoint_id,
                       const sql_column_postgis_point2d& point,
                       const sql_column_float& angle,
                       const sql_column_int& octave,
                       const sql_column_double& disparity,
                       const sql_column_double& depth,
                       const sql_column_uuid& landmark_id,
                       const sql_column_uuid& keyframe_id,
                       const sql_column_uuid& map_id);

    const sql_column_uuid keypoint_id;
    const sql_column_postgis_point2d point;
    const sql_column_float angle;
    const sql_column_int octave;
    const sql_column_double disparity;
    const sql_column_double depth;
    const sql_column_uuid landmark_id;
    const sql_column_uuid keyframe_id;
    const sql_column_uuid map_id;

protected:
};

class sql_descriptor_table : public sql_table {
public:
    sql_descriptor_table();
    sql_descriptor_table(const sql_column_uuid& descriptor_id,
                         const sql_column_json& data,
                         const sql_column_uuid& keypoint_id);

    const sql_column_uuid descriptor_id;
    const sql_column_json data;
    const sql_column_uuid keypoint_id;

protected:
};

class sql_keyframe_table : public sql_table {
public:
    sql_keyframe_table();
    sql_keyframe_table(const sql_column_uuid& keyframe_id,
                       const sql_column_timestamp& timestamp,
                       const sql_column_float& depth_threshold,
                       const sql_column_json& rotation_cw,
                       const sql_column_json& translation_cw,
                       const sql_column_int& number_of_scale_levels,
                       const sql_column_float& scale_factor,
                       const sql_column_uuid& parent_id,
                       const sql_column_uuid& source_frame_id,
                       const sql_column_uuid& map_id,
                       const sql_column_uuid& camera_rig_id);

    const sql_column_uuid keyframe_id;
    const sql_column_timestamp timestamp;
    const sql_column_float depth_threshold;
    const sql_column_json rotation_cw;
    const sql_column_json translation_cw;
    const sql_column_int number_of_scale_levels;
    const sql_column_float scale_factor;
    const sql_column_uuid parent_id;
    const sql_column_uuid source_frame_id;
    const sql_column_uuid map_id;
    const sql_column_uuid camera_rig_id;

protected:
};

class sql_map_table : public sql_table {
public:
    sql_map_table();
    sql_map_table(const sql_column_uuid& map_id,
                  const sql_column_text& name,
                  const sql_column_timestamp& valid_until);

    const sql_column_uuid map_id;
    const sql_column_text name;
    const sql_column_timestamp valid_until;

protected:
};

class sql_camera_rig_table : public sql_table {
public:
    sql_camera_rig_table();
    sql_camera_rig_table(const sql_column_uuid& camera_rig_id,
                         const sql_column_text& name);

    const sql_column_uuid camera_rig_id;
    const sql_column_text name;

protected:
};

class sql_loop_edge_table : public sql_table {
public:
    sql_loop_edge_table();
    sql_loop_edge_table(const sql_column_uuid& loop_edge_table_pk,
                        const sql_column_uuid& loop_edge_id,
                        const sql_column_uuid& keyframe_id);

    const sql_column_uuid loop_edge_table_pk;
    const sql_column_uuid loop_edge_id;
    const sql_column_uuid keyframe_id;

protected:
};

class sql_child_keyframe_table : public sql_table {
public:
    sql_child_keyframe_table();
    sql_child_keyframe_table(const sql_column_uuid& child_keyframe_table_pk,
                             const sql_column_uuid& child_keyframe_id,
                             const sql_column_uuid& keyframe_id);

    const sql_column_uuid child_keyframe_table_pk;
    const sql_column_uuid child_keyframe_id;
    const sql_column_uuid keyframe_id;

protected:
};

std::string create_insert(const sql_table& table,
                          const std::map<const sql_column, std::string>& key_value_pairs);
std::string create_select(const std::vector<sql_select_identifier>& cols,
                              bool distinct,
                              const sql_table& from,
                              const std::vector<std::pair<const sql_table, std::pair<const sql_column, const sql_column>>>& join_on,
                              const std::string& where_clause);

std::string add_single_quotes(const std::string& input);
std::string get_postgis_point(double x, double y);
std::string get_postgis_point(double x, double y, double z);

namespace default_tables {
static sql_camera_table camera_table;
static sql_map_table map_table;
static sql_landmark_table landmark_table;
static sql_keypoint_table keypoint_table;
static sql_descriptor_table descriptor_table;
static sql_keyframe_table keyframe_table;
static sql_camera_rig_table camera_rig_table;
static sql_loop_edge_table loop_edge_table;
static sql_child_keyframe_table child_keyframe_table;
} // namespace default_tables

} // namespace postgres
} // namespace util
