//
// Created by ernst on 6/9/22.
//

#ifndef POSTGRES_UTILS_CAMERADTO_HPP
#define POSTGRES_UTILS_CAMERADTO_HPP

#include "dto/SensorDto.hpp"
#include "oatpp/core/Types.hpp"
#include "oatpp/core/macro/codegen.hpp"

#include OATPP_CODEGEN_BEGIN(DTO)

class CameraDto : public SensorDto {
  DTO_INIT(CameraDto, SensorDto)

  DTO_FIELD(UInt16, camera_id, 0);
  DTO_FIELD(String, description, "description") = "A Camera";
  DTO_FIELD(Enum<Type>::AsString, type, "type") = Type::CAMERA;
};

#include OATPP_CODEGEN_END(DTO)

#endif  // POSTGRES_UTILS_CAMERADTO_HPP
