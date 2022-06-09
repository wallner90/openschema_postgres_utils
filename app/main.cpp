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

  auto new_camera_rig = oatpp::Object<CameraRigDto>::createShared();
  new_camera_rig->description = std::string("TestRigFromCode");
  //m_database->createCameraRig("TestDescriptionFromString");

  m_database->createCameraRig(new_camera_rig);

  auto dbResult = m_database->getAllCameraRigs(0u, 100u);
  if (dbResult->isSuccess()) {
      auto result = dbResult->fetch<oatpp::Vector<oatpp::Object<CameraRigDto>>>();

      std::cout << "THERE ARE " << result->size() << " CAMERA RIG ENTRIES IN THE DB" << std::endl;

      for (auto camera_rig: *result) {
          oatpp::String json = jsonObjectMapper->writeToString(camera_rig);
          std::cout << json->c_str() << std::endl;
      }
  } else {
      std::cout << "COULD NOT QUERY ALL CAMERA RIGS!" << std::endl;
  }

  return 0;
}
