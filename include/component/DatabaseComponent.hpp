#ifndef EXAMPLE_POSTGRESQL_DATABASECOMPONENT_HPP
#define EXAMPLE_POSTGRESQL_DATABASECOMPONENT_HPP

#include "db/openSchemaDb.hpp"
#include "oatpp/core/macro/component.hpp"

class DatabaseComponent {
 public:
  /**
   * Create database client
   */
  OATPP_CREATE_COMPONENT(std::shared_ptr<OpenSchemaDb>, openSchemaDb)
  ([] {
    /* Create database-specific ConnectionProvider */
    auto connectionProvider =
        std::make_shared<oatpp::postgresql::ConnectionProvider>(
            "postgresql://postgres:postgres@localhost:5432/postgres");

    /* Create database-specific ConnectionPool */
    auto connectionPool = oatpp::postgresql::ConnectionPool::createShared(
        connectionProvider, 10 /* max-connections */,
        std::chrono::seconds(5) /* connection TTL */);

    /* Create database-specific Executor */
    auto executor =
        std::make_shared<oatpp::postgresql::Executor>(connectionPool);

    /* Create MyClient database client */
    return std::make_shared<OpenSchemaDb>(executor);
  }());
};

#endif  // EXAMPLE_POSTGRESQL_DATABASECOMPONENT_HPP