//
// Created by ernst on 6/9/22.
//

#ifndef POSTGRES_UTILS_SENSORDTO_HPP
#define POSTGRES_UTILS_SENSORDTO_HPP

#include "dto/SensorTypes.hpp"
#include "oatpp/core/Types.hpp"
#include "oatpp/core/macro/codegen.hpp"
#include "oatpp-postgresql/mapping/type/Uuid.hpp"

#include OATPP_CODEGEN_BEGIN(DTO)

class SensorDto : public oatpp::DTO {
  DTO_INIT(SensorDto, DTO)

  DTO_FIELD(oatpp::postgresql::mapping::type::Uuid, id, "sensor_id");
  DTO_FIELD(oatpp::postgresql::mapping::type::Uuid, posegraph_id, "posegraph_id_posegraph");
  DTO_FIELD(String, topic, "topic");
  DTO_FIELD(String, description, "description") = "A Generic Sensor";
  SensorTypes type{SensorTypes::NONE};
};

#include OATPP_CODEGEN_END(DTO)

#endif  // POSTGRES_UTILS_SENSORDTO_HPP
