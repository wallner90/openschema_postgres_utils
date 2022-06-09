//
// Created by ernst on 6/9/22.
//

#ifndef POSTGRES_UTILS_SENSORDTO_HPP
#define POSTGRES_UTILS_SENSORDTO_HPP

#include "oatpp/core/macro/codegen.hpp"
#include "oatpp/core/Types.hpp"
#include "dto/SensorTypes.hpp"

#include OATPP_CODEGEN_BEGIN(DTO)


class SensorDto : public oatpp::DTO {

    DTO_INIT(SensorDto, DTO)

    DTO_FIELD(String, id);
    DTO_FIELD(String, topic);
    DTO_FIELD(String, description, "a virtual sensor");
    DTO_FIELD(Enum<Type>::AsString, type, "NONE");

};

#include OATPP_CODEGEN_END(DTO)


#endif //POSTGRES_UTILS_SENSORDTO_HPP
