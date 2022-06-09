// Executables must have the following defined if the library contains
// doctest definitions. For builds with this disabled, e.g. code shipped to
// users, this can be left out.
#ifdef ENABLE_DOCTEST_IN_LIBRARY
#define DOCTEST_CONFIG_IMPLEMENT
#include "doctest/doctest.h"
#endif

#include <iostream>
#include <stdlib.h>

#include "exampleConfig.h"
#include "postgres_utils.h"

#include "component/DatabaseComponent.hpp"


int main()
{

  // Oat++ Minimal example
  DatabaseComponent databaseComponent;
  OATPP_COMPONENT(std::shared_ptr<UserDb>, m_database); // Inject database component

  auto dbResult = m_database->getUserById("f400368f-1762-48f9-a8e1-2293d6298016");
  auto result = dbResult->fetch<oatpp::Vector<oatpp::Object<UserDto>>>();
  auto user = result[0];
  auto role = user->role;
  std::cout << "E-Mail: " << *(user->email) << std::endl;


  auto new_user = oatpp::Object<UserDto>::createShared();
  new_user->email = "test@test.com";
  new_user->userName = "testUser123";
  new_user->password = "password123";
  new_user->role = Role::ADMIN;
  m_database->createUser(new_user);


  return 0;


 

  std::cout << "### PostgreSQL Utils demo v"
            << PROJECT_VERSION_MAJOR
            << "."
            << PROJECT_VERSION_MINOR
            << "."
            << PROJECT_VERSION_PATCH
            << "."
            << PROJECT_VERSION_TWEAK
            << " ###"
            << std::endl
            << std::endl;

  { // Examples: Using postgres util namespace for convenient access
    using namespace util::postgres::default_tables;
    std::cout << "## SELECT EXAMPLES ##" << std::endl;
    {
      const auto map_name = "map";
      std::cout << "# EXAMPLE: Select all keyframes in current map \"" << map_name << "\":" << std::endl;
      const auto select_statement = util::postgres::create_select(
          {keyframe_table.keyframe_id.get_sql_identifier(),
           keyframe_table.timestamp.get_sql_identifier(),
           keyframe_table.timestamp.get_sql_identifier_as_timestamp_float(),
           keyframe_table.depth_threshold.get_sql_identifier(),
           keyframe_table.rotation_cw.get_sql_identifier_as_text(),
           keyframe_table.translation_cw.get_sql_identifier_as_text(),
           keyframe_table.number_of_scale_levels.get_sql_identifier(),
           keyframe_table.scale_factor.get_sql_identifier(),
           keyframe_table.parent_id.get_sql_identifier(),
           camera_rig_table.name.get_sql_identifier().renamed_to("camera_name")},
          true,
          map_table,
          {{keyframe_table, {keyframe_table.map_id, map_table.map_id}},
           {camera_rig_table, {camera_rig_table.camera_rig_id, keyframe_table.camera_rig_id}},
           {camera_table, {camera_table.camera_rig_id, camera_rig_table.camera_rig_id}}},
          map_table.name.get_full_qualified_name() + " = " + util::postgres::add_single_quotes(map_name));
      std::cout << select_statement << std::endl
                << std::endl;
    }

    {
      const auto keyframe_uuid = "85069c34-daa3-11ec-9d64-0242ac120002";
      std::cout << "# EXAMPLE: Select all keypoints of keyframe with uuid \"" << keyframe_uuid << "\":" << std::endl;

      const auto select_statement = util::postgres::create_select(
          {keypoint_table.keypoint_id.get_sql_identifier(),
           keypoint_table.point.get_sql_identifier_x().renamed_to("point_u"),
           keypoint_table.point.get_sql_identifier_y().renamed_to("point_v"),
           keypoint_table.angle.get_sql_identifier(),
           keypoint_table.octave.get_sql_identifier(),
           keypoint_table.disparity.get_sql_identifier(),
           keypoint_table.depth.get_sql_identifier(),
           descriptor_table.data.get_sql_identifier_as_text().renamed_to("descriptor_json")},
          true,
          keypoint_table,
          {{descriptor_table, {descriptor_table.keypoint_id, keypoint_table.keypoint_id}}},
          keypoint_table.keyframe_id.get_full_qualified_name() + " = uuid(" + util::postgres::add_single_quotes(keyframe_uuid) + ")");
      std::cout << select_statement << std::endl
                << std::endl;
    }

    {
      const auto map_name = "map";
      std::cout << "# EXAMPLE: Select all landmarks in current map \"" << map_name << "\":" << std::endl;
      const auto select_statement = util::postgres::create_select(
          {landmark_table.landmark_id.get_sql_identifier(),
           landmark_table.position.get_sql_identifier_x().renamed_to("pos_x"),
           landmark_table.position.get_sql_identifier_y().renamed_to("pos_y"),
           landmark_table.position.get_sql_identifier_z().renamed_to("pos_z"),
           landmark_table.first_keyframe_id.get_sql_identifier(),
           landmark_table.reference_keyframe_id.get_sql_identifier(),
           landmark_table.num_observable.get_sql_identifier(),
           landmark_table.num_observed.get_sql_identifier()},
          true,
          map_table,
          {{landmark_table, {landmark_table.map_id, map_table.map_id}}},
          map_table.name.get_full_qualified_name() + " = " + util::postgres::add_single_quotes(map_name));
      std::cout << select_statement << std::endl
                << std::endl;
    }

    {
      const auto keyframe_uuid = "85069c34-daa3-11ec-9d64-0242ac120002";
      std::cout << "# EXAMPLE: Select all landmarks with keypoints in keyframe with uuid \"" << keyframe_uuid << "\":" << std::endl;
      const auto select_statement = util::postgres::create_select(
          {keypoint_table.keypoint_id.get_sql_identifier(),
           landmark_table.landmark_id.get_sql_identifier()},
          true,
          keypoint_table,
          {{landmark_table, {landmark_table.landmark_id, keypoint_table.landmark_id}}},
          keypoint_table.keyframe_id.get_full_qualified_name() + " = uuid(" + util::postgres::add_single_quotes(keyframe_uuid) + ")");
      std::cout << select_statement << std::endl
                << std::endl;
    }

    std::cout << "## INSERT EXAMPLES ##" << std::endl;
    {
      const auto map_uuid = "2fadeba0-daa5-11ec-9d64-0242ac120002";
      const auto map_name = "map2";
      std::cout << "# Example: Insert map with uuid " << map_uuid << " and name " << map_name << " into database:" << std::endl;
      const auto insert_statement = util::postgres::create_insert(
          map_table,
          {{map_table.map_id, util::postgres::add_single_quotes(map_uuid)},
           {map_table.name, util::postgres::add_single_quotes(map_name)}});
      std::cout << insert_statement << std::endl
                << std::endl;
    }

    {
      const auto map_uuid = "2fadeba0-daa5-11ec-9d64-0242ac120002";
      const auto keyframe_uuid = "85069c34-daa3-11ec-9d64-0242ac120002";
      const auto camera_rig_uuid = "938cd83c-daa3-11ec-9d64-0242ac120002";
      const auto timestamp = 12345.6789;
      const auto depth_thr = 5.0;
      const auto num_scale_levels = 5u;
      const auto scale_factor = 1u;

      std::cout << "# Example: Insert keyframe with uuid " << keyframe_uuid << " and its cols into database:" << std::endl;
      const auto insert_statement = util::postgres::create_insert(
          keyframe_table,
          {{keyframe_table.keyframe_id, util::postgres::add_single_quotes(keyframe_uuid)},
           {keyframe_table.parent_id, "NULL"},
           {keyframe_table.timestamp, "to_timestamp(" + std::to_string(timestamp) + ")"},
           {keyframe_table.depth_threshold, std::to_string(depth_thr)},
           {keyframe_table.rotation_cw, util::postgres::add_single_quotes("Rotation as JSON BLOB...")},
           {keyframe_table.translation_cw, util::postgres::add_single_quotes("Translation as JSON BLOB...")},
           {keyframe_table.number_of_scale_levels, std::to_string(num_scale_levels)},
           {keyframe_table.scale_factor, std::to_string(scale_factor)},
           {keyframe_table.map_id, util::postgres::add_single_quotes(map_uuid)},
           {keyframe_table.camera_rig_id, util::postgres::add_single_quotes(camera_rig_uuid)}});
      std::cout << insert_statement << std::endl
                << std::endl;
    }
  }
}
