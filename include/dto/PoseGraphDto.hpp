//
// Created by ernst on 6/10/22.
//

#ifndef POSTGRES_UTILS_POSEGRAPHDTO_HPP
#define POSTGRES_UTILS_POSEGRAPHDTO_HPP

#include "dto/SensorDto.hpp"
#include "oatpp/core/Types.hpp"
#include "oatpp/core/macro/codegen.hpp"
#include "oatpp-postgresql/mapping/type/Uuid.hpp"

#include OATPP_CODEGEN_BEGIN(DTO)

class PoseGraphDto : public oatpp::DTO {
  DTO_INIT(PoseGraphDto, oatpp::DTO)
  DTO_FIELD(oatpp::postgresql::mapping::type::Uuid, posegraph_id, "posegraph_id");
  DTO_FIELD(String, description, "description");
  DTO_FIELD(oatpp::postgresql::mapping::type::Uuid, base_sensor_id, "base_sensor_id");
};

#include OATPP_CODEGEN_END(DTO)

#endif  // POSTGRES_UTILS_POSEGRAPHDTO_HPP
