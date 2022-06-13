//
// Created by ernst on 6/9/22.
//

#ifndef POSTGRES_UTILS_CAMERARIGDTO_HPP
#define POSTGRES_UTILS_CAMERARIGDTO_HPP

#include "dto/CameraDto.hpp"
#include "oatpp/core/Types.hpp"
#include "oatpp/core/macro/codegen.hpp"

#include OATPP_CODEGEN_BEGIN(DTO)

class CameraRigDto : public oatpp::DTO {
  DTO_INIT(CameraRigDto, oatpp::DTO)

  DTO_FIELD(String, camera_rig_id, "camera_rig_id");
  DTO_FIELD(String, description, "description");
  // DTO_FIELD(List<Object<CameraDto>>,  cameras);  // a camera rig has a list
  // of cameras - is this the right
  //                      // way to encode that?
};

#include OATPP_CODEGEN_END(DTO)

#endif  // POSTGRES_UTILS_CAMERARIGDTO_HPP
