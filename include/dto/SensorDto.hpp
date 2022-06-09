//
// Created by ernst on 6/9/22.
//

#ifndef POSTGRES_UTILS_SENSORDTO_HPP
#define POSTGRES_UTILS_SENSORDTO_HPP

#include "dto/SensorTypes.hpp"
#include "oatpp/core/Types.hpp"
#include "oatpp/core/macro/codegen.hpp"

#include OATPP_CODEGEN_BEGIN(DTO)

class SensorDto : public oatpp::DTO {
  DTO_INIT(SensorDto, DTO)

  DTO_FIELD(String, id);
  DTO_FIELD(String, topic);
  DTO_FIELD(String, description, "description") = "A Generic Sensor";
  DTO_FIELD(Enum<Type>::AsString, type, "type") = Type::NONE;
};

#include OATPP_CODEGEN_END(DTO)

#endif  // POSTGRES_UTILS_SENSORDTO_HPP
