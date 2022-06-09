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

#include "oatpp/parser/json/mapping/ObjectMapper.hpp"
#include "component/DatabaseComponent.hpp"


int main()
{

  // Oat++ Minimal example
  DatabaseComponent databaseComponent;
  auto jsonObjectMapper = oatpp::parser::json::mapping::ObjectMapper::createShared();

  OATPP_COMPONENT(std::shared_ptr<UserDb>, m_database); // Inject database component


  auto new_user = oatpp::Object<UserDto>::createShared();
  new_user->email = "test@test.com";
  new_user->userName = "testUser123";
  new_user->password = "password123";
  new_user->role = Role::ADMIN;
  m_database->createUser(new_user);

    std::string queryID;

    auto dbResult = m_database->getAllUsers(0u, 100);

    if(dbResult->isSuccess()) {
            auto result = dbResult->fetch<oatpp::Vector<oatpp::Object<UserDto>>>();

            std::cout << "THERE ARE " << result->size() << " USER ENTRIES IN THE DB" << std::endl;

            for (auto user: *result) {
                oatpp::String json = jsonObjectMapper->writeToString(user);
                std::cout << json->c_str() << std::endl;

                queryID = user->userName;
            }

    } else {
        std::cout << "COULD NOT QUERY DB!" << std::endl;
    }


  dbResult = m_database->getUserById(queryID);

  if(dbResult->isSuccess()) {
      auto result = dbResult->fetch<oatpp::Vector<oatpp::Object<UserDto>>>();

      std::cout << "QUERY FOR " << queryID << " RETURNED " << result->size() << " MATCHES" << std::endl;

      for (auto user: *result) {
          oatpp::String json = jsonObjectMapper->writeToString(user);
          std::cout << json->c_str() << std::endl;
      }
  } else {
      std::cout << "COULD NOT QUERY DB!" << std::endl;
  }

  return 0;

}
