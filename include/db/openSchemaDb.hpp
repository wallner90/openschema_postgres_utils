#ifndef EXAMPLE_POSTGRESQL_OpenSchemaDb_HPP
#define EXAMPLE_POSTGRESQL_OpenSchemaDb_HPP

#include "dto/CameraRigDto.hpp"
#include "dto/ImuDto.hpp"
#include "dto/PoseGraphDto.hpp"
#include "dto/UserDto.hpp"
#include "dto/VertexDto.hpp"
#include "oatpp-postgresql/orm.hpp"
#include "types/Point.hpp"

#include OATPP_CODEGEN_BEGIN(DbClient)  //<- Begin Codegen

/**
 * OpenSchemaDb client definitions.
 */
class OpenSchemaDb : public oatpp::orm::DbClient {
 public:
  OpenSchemaDb(const std::shared_ptr<oatpp::orm::Executor>& executor)
      : oatpp::orm::DbClient(executor) {
    oatpp::orm::SchemaMigration migration(executor);
    setEnabledInterpretations({"postgresql", "postgis"});
    migration.addFile(1 /* start from version 1 */,
                      "/workspaces/openschema_postgres_utils/sql/"
                      "db_schema_postGIS_fixed.sql");
    // migration.addFile(2 /* start from version 1 */,
    // "/home/ernst/Documents/Iviso/_OpenSCHEMA/openschema_postgres_utils/sql/002_fill.sql");
    // TODO - Add more migrations here.
    migration.migrate();  // <-- run migrations. This guy will throw on error.

    auto version = executor->getSchemaVersion();
    OATPP_LOGD("openSchemaDb", "Migration - OK. Version=%d.", version);
  }

  // create a posegraph with a specific base sensor
  QUERY(createPosegraph,
        "INSERT INTO posegraph "
        "(description) "
        "VALUES (:posegraph.description) "
        "RETURNING *;",
        PREPARE(true), PARAM(oatpp::Object<PoseGraphDto>, posegraph))

  // create a vertex
  QUERY(createVertex,
        "INSERT INTO vertex (position, posegraph_id_posegraph) "
        "VALUES "
        "(:vertex.position, :posegraph.posegraph_id) "
        "RETURNING *;",
        PREPARE(true), PARAM(oatpp::Object<PoseGraphDto>, posegraph),
        PARAM(oatpp::Object<VertexDto>, vertex))

  // create an IMU that is also a sensor
  QUERY(createIMU,
        "INSERT INTO imu"
        "(description, posegraph_id_posegraph) VALUES "
        "(:imu.description, :posegraph.posegraph_id)"
        ";",
        PREPARE(true), PARAM(oatpp::Object<ImuDto>, imu),
        PARAM(oatpp::Object<PoseGraphDto>, posegraph))

  QUERY(createCameraRig,
        "INSERT INTO camera_rig"
        "(camera_rig_id, description) VALUES "
        "uuid_generate_v4(), (:camera_rig.description)"
        "RETURNING *;",
        PREPARE(true), PARAM(oatpp::Object<CameraRigDto>, camera_rig))

  QUERY(getAllCameraRigs,
        "SELECT * FROM camera_rig LIMIT :limit OFFSET :offset;",
        PREPARE(true),  //<-- user prepared statement!
        PARAM(oatpp::UInt32, offset), PARAM(oatpp::UInt32, limit))

  QUERY(createUser,
        "INSERT INTO AppUser"
        "(username, email, password, role) VALUES "
        "(:user.username, :user.email, :user.password, "
        ":user.role)"
        "RETURNING *;",
        PREPARE(true),  // user prepared statement!
        PARAM(oatpp::Object<UserDto>, user))

  QUERY(updateUser,
        "UPDATE AppUser "
        "SET "
        " username=:user.username, "
        " email=:user.email, "
        " password=:user.password, "
        " role=:user.role "
        "WHERE "
        " id=:user.id "
        "RETURNING *;",
        PREPARE(true),  //<-- user prepared statement!
        PARAM(oatpp::Object<UserDto>, user))

  QUERY(getUserById, "SELECT * FROM AppUser WHERE id=:id;",
        PREPARE(true),  //<-- user prepared statement!
        PARAM(oatpp::postgresql::mapping::type::Uuid, id))

  //   QUERY(getAllUsers, "SELECT * FROM AppUser LIMIT :limit OFFSET :offset;",
  //         PREPARE(true),  //<-- user prepared statement!
  //         PARAM(oatpp::UInt32, offset), PARAM(oatpp::UInt32, limit))

  QUERY(getAllUsers, "SELECT * FROM AppUser;", PREPARE(true))

  QUERY(deleteUserById, "DELETE FROM AppUser WHERE id=:id;",
        PREPARE(true),  //<-- user prepared statement!
        PARAM(oatpp::String, id))
};

#include OATPP_CODEGEN_END(DbClient)  //<- End Codegen

#endif  // EXAMPLE_POSTGRESQL_OpenSchemaDb_HPP