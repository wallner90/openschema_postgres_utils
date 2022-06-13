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
#include "types/Point.hpp"
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

  {
    auto all_users_db_result = m_database->getAllUsers();
    if (all_users_db_result->isSuccess()) {
      auto fetched_created_users =
          created_user->fetch<oatpp::Vector<oatpp::Object<UserDto>>>();
      std::cout << "Found " << fetched_created_users->size() << " users"
                << std::endl;
      for (auto created_user_it : *fetched_created_users) {
        std::cout << "created user has id" << *(created_user_it->userName)
                  << std::endl;
      }
    }
  }


  {
    oatpp::postgresql::mapping::type::UuidObject uuid(
        "1be236cb-f2cb-4707-9c24-35c54d8a1c59");
    auto dbResult = m_database->getUserById(uuid);
    auto result = dbResult->fetch<oatpp::Vector<oatpp::Object<UserDto>>>();
    if (result->size()) {
      auto user0 = result[0];
      std::cout << "E-Mail: " << *(user0->email) << std::endl;
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

  int numVerts = 10;
  for (int i=0; i<numVerts; i++) {

      oatpp::postgresql::mapping::type::Point currentPoint ({static_cast<v_float32>(i), 0.0});

      auto currentVertex = oatpp::Object<VertexDto>::createShared();
      currentVertex->position = currentPoint;
      //currentVertex->position = {{"x", currentPoint->x}, {"y", currentPoint->y}, {"z", currentPoint->z}};
      // currentVertex->position = currentPoint.toString();

      std::cout << currentPoint->toString()->c_str() << std::endl;

      auto query = m_database->createVertex(main_pose_graph, currentVertex);
      if (not query->isSuccess())
        std::cout << query->getErrorMessage()->c_str() << std::endl;

    if (i>0) {
        std::cout << "adding edge between vertex #" << i-1 << " and #" << i << std::endl;

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
