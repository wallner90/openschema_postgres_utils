//
// Created by ernst on 6/9/22.
//

#ifndef POSTGRES_UTILS_IMUDTO_HPP
#define POSTGRES_UTILS_IMUDTO_HPP

#include "dto/SensorDto.hpp"
#include "oatpp/core/Types.hpp"
#include "oatpp/core/macro/codegen.hpp"

#include OATPP_CODEGEN_BEGIN(DTO)

class ImuDto : public SensorDto {
  DTO_INIT(ImuDto, SensorDto)
  
  ImuDto()
  {
    type = SensorTypes::IMU;
    description = "An IMU";
  }
};

#include OATPP_CODEGEN_END(DTO)

#endif  // POSTGRES_UTILS_IMUDTO_HPP
