//
// Created by ernst on 6/9/22.
//

#ifndef POSTGRES_UTILS_IMUDTO_HPP
#define POSTGRES_UTILS_IMUDTO_HPP

#include "oatpp/core/macro/codegen.hpp"
#include "oatpp/core/Types.hpp"
#include "dto/SensorDto.hpp"

#include OATPP_CODEGEN_BEGIN(DTO)

class ImuDto : public SensorDto {

    DTO_INIT(ImuDto, SensorDto)
    DTO_FIELD(String, description, "an IMU");
    DTO_FIELD(Enum<Type>::AsString, type, "IMU");

};

#include OATPP_CODEGEN_END(DTO)


#endif //POSTGRES_UTILS_IMUDTO_HPP
