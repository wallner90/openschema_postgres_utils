#ifndef EXAMPLE_POSTGRESQL_OpenSchemaDb_HPP
#define EXAMPLE_POSTGRESQL_OpenSchemaDb_HPP

#include "dto/UserDto.hpp"
#include "dto/CameraRigDto.hpp"
#include "oatpp-postgresql/orm.hpp"

#include OATPP_CODEGEN_BEGIN(DbClient)  //<- Begin Codegen

/**
 * OpenSchemaDb client definitions.
 */
class OpenSchemaDb : public oatpp::orm::DbClient {
 public:
  OpenSchemaDb(const std::shared_ptr<oatpp::orm::Executor>& executor)
      : oatpp::orm::DbClient(executor) {
    oatpp::orm::SchemaMigration migration(executor);
    migration.addFile(1 /* start from version 1 */,
                      "/workspaces/openschema_postgres_utils/sql/001_init.sql");
    // migration.addFile(2 /* start from version 1 */,
    // "/home/ernst/Documents/Iviso/_OpenSCHEMA/openschema_postgres_utils/sql/002_fill.sql");
    // TODO - Add more migrations here.
    migration.migrate();  // <-- run migrations. This guy will throw on error.

    auto version = executor->getSchemaVersion();
    OATPP_LOGD("openSchemaDb", "Migration - OK. Version=%d.", version);
  }

//   QUERY(createCameraRig,
//         "INSERT INTO camera_rig"
//         "(description) VALUES "
//         "(:camera_rig.description)"
//         "RETURNING *;",
//         PREPARE(true),
//         PARAM(oatpp::Object<CameraRigDto>, camera_rig))

  QUERY(createCameraRig,
        "INSERT INTO camera_rig"
        "(description) VALUES "
        "(camera_rig_description)"
        "RETURNING *;",
        PREPARE(true),
        PARAM(oatpp::String, camera_rig_description))

  QUERY(createUser,
        "INSERT INTO AppUser"
        "(id, username, email, password, role) VALUES "
        "(uuid_generate_v4(), :user.username, :user.email, :user.password, "
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
        PARAM(oatpp::String, id))

  QUERY(getAllUsers, "SELECT * FROM AppUser LIMIT :limit OFFSET :offset;",
        PREPARE(true),  //<-- user prepared statement!
        PARAM(oatpp::UInt32, offset), PARAM(oatpp::UInt32, limit))

  QUERY(deleteUserById, "DELETE FROM AppUser WHERE id=:id;",
        PREPARE(true),  //<-- user prepared statement!
        PARAM(oatpp::String, id))
};

#include OATPP_CODEGEN_END(DbClient)  //<- End Codegen

#endif  // EXAMPLE_POSTGRESQL_OpenSchemaDb_HPP