
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
#include "types/Point.hpp"

int main() {
  // Oat++ Minimal example
  DatabaseComponent databaseComponent;
  auto jsonObjectMapper =
      oatpp::parser::json::mapping::ObjectMapper::createShared();

  OATPP_COMPONENT(std::shared_ptr<OpenSchemaDb>,
                  m_database);  // Inject database component

  // create empty posegraph
  auto main_pose_graph = oatpp::Object<PoseGraphDto>::createShared();
  main_pose_graph->description = "the main posegraph";
  // add pose graph to DB
  auto posegraph_results =
      m_database->createPosegraph(main_pose_graph)
          ->fetch<oatpp::Vector<oatpp::Object<PoseGraphDto>>>();

  // create an IMU
  auto imu = oatpp::Object<ImuDto>::createShared();
  imu->description = "an imu";
  // add imu to DB (and add to posegraph, i.e., one posegraph has 1-n IMUs)
  auto sensor_results = m_database->createIMU(imu, posegraph_results[0])
                            ->fetch<oatpp::Vector<oatpp::Object<ImuDto>>>();

  int numVerts = 10;
  for (int i = 0; i < numVerts; i++) {
    oatpp::postgresql::mapping::type::Point currentPoint(
        {static_cast<v_float32>(i), 0.0});

    std::cout << "ADDING NEW VERTX TO POSE GRAPH "
              << posegraph_results[0]->posegraph_id->toString()->c_str()
              << std::endl;

    auto currentVertex = oatpp::Object<VertexDto>::createShared();
    currentVertex->position = currentPoint;

    // THIS WORKS
    auto vertex_add =
        m_database
            ->createVertexFromString(posegraph_results[0],
                                     currentVertex->position->toString(),
                                     oatpp::UInt16(4326))
            ->fetch<oatpp::Vector<oatpp::Object<VertexDto>>>();


    // std::cout << "Added vertex with ID "
    //           << vertex_results[0]->vertex_id->toString()->c_str() << std::endl;

    // // THIS DOESNT
    // query = m_database->createVertex(posegraph_results[0], currentVertex,
    // oatpp::UInt16 (4326)); if (not query->isSuccess())
    //   std::cout << query->getErrorMessage()->c_str() << std::endl;

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
