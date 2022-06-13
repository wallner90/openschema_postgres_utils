// Executables must have the following defined if the library contains
// doctest definitions. For builds with this disabled, e.g. code shipped to
// users, this can be left out.
//#ifdef ENABLE_DOCTEST_IN_LIBRARY
//#define DOCTEST_CONFIG_IMPLEMENT
//#include "doctest/doctest.h"
//#endif

#include <stdlib.h>

#include <iostream>

#include "component/DatabaseComponent.hpp"
#include "exampleConfig.h"
#include "oatpp/parser/json/mapping/ObjectMapper.hpp"
#include "postgres_utils.h"

int main() {
  // Oat++ Minimal example
  DatabaseComponent databaseComponent;
  auto jsonObjectMapper =
      oatpp::parser::json::mapping::ObjectMapper::createShared();

  OATPP_COMPONENT(std::shared_ptr<OpenSchemaDb>,
                  m_database);  // Inject database component

  // uuid tests
  auto user = oatpp::Object<UserDto>::createShared();
  user->userName = "test_user3";
  user->email = "test3@test.com";
  user->password = "test12345";
  user->role = Role::GUEST;

  auto created_user = m_database->createUser(user);

  auto all_users_db_result = m_database->getAllUsers(0u, 100u);
  if (all_users_db_result->isSuccess()) {
    auto fetched_created_users =
        created_user->fetch<oatpp::Vector<oatpp::Object<UserDto>>>();
    for (auto created_user : *fetched_created_users) {
      std::cout << "created user has id" << *(created_user->userName)
                << std::endl;
    }
  }

  // create an IMU to serve as base sensor for the posegraph
  auto imu = oatpp::Object<ImuDto>::createShared();
  imu->description = "an imu";

  // add imu to DB
  m_database->createIMU(imu);

  // create empty posegraph
  auto main_pose_graph = oatpp::Object<PoseGraphDto>::createShared();
  main_pose_graph->description = "the main posegraph";
  main_pose_graph->base_sensor = imu;

  // add pose graph to DB
  m_database->createPosegraph(main_pose_graph, main_pose_graph->base_sensor);

  // add a couple of vertices, with edges between consecutive ones
  int numVerts = 10;
  for (int i = 0; i < numVerts; i++) {
    std::cout << "adding vertex #" << i << std::endl;
    if (i > 0) {
      std::cout << "adding edge between vertex #" << i - 1 << " and #" << i
                << std::endl;
    }
  }

  return 0;

  auto new_camera_rig = oatpp::Object<CameraRigDto>::createShared();
  new_camera_rig->description = std::string("TestRigFromCode");
  // m_database->createCameraRig("TestDescriptionFromString");

  m_database->createCameraRig(new_camera_rig);

  auto dbResult = m_database->getAllCameraRigs(0u, 100u);
  if (dbResult->isSuccess()) {
    auto result = dbResult->fetch<oatpp::Vector<oatpp::Object<CameraRigDto>>>();

    std::cout << "THERE ARE " << result->size()
              << " CAMERA RIG ENTRIES IN THE DB" << std::endl;

    for (auto camera_rig : *result) {
      oatpp::String json = jsonObjectMapper->writeToString(camera_rig);
      std::cout << json->c_str() << std::endl;
    }
  } else {
    std::cout << "COULD NOT QUERY ALL CAMERA RIGS!" << std::endl;
  }

  return 0;
}
