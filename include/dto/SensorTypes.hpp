//
// Created by ernst on 6/9/22.
//

#ifndef POSTGRES_UTILS_SENSORTYPES_HPP
#define POSTGRES_UTILS_SENSORTYPES_HPP

#include "oatpp/core/macro/codegen.hpp"
#include "oatpp/core/Types.hpp"

#include OATPP_CODEGEN_BEGIN(DTO)

ENUM(SensorTypes, v_int32,
     VALUE(NONE, 0, "NONE"),
     VALUE(CAMERA, 1, "CAMERA"),
     VALUE(IMU, 2, "IMU")
)

#include OATPP_CODEGEN_END(DTO)

#endif //POSTGRES_UTILS_SENSORTYPES_HPP
