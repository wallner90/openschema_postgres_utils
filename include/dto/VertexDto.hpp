//
// Created by ernst on 13.06.22.
//

#ifndef POSTGRES_UTILS_VERTEXDTO_HPP
#define POSTGRES_UTILS_VERTEXDTO_HPP

#include "oatpp/core/Types.hpp"
#include "oatpp-postgresql/mapping/type/Uuid.hpp"
#include "oatpp/core/macro/codegen.hpp"
#include "types/Point.hpp"

#include OATPP_CODEGEN_BEGIN(DTO)

class VertexDto : public oatpp::DTO {
  DTO_INIT(VertexDto, oatpp::DTO)

  DTO_FIELD(oatpp::postgresql::mapping::type::Uuid, vertex_id, "vertex_id");
  // DTO_FIELD(oatpp::UnorderedFields<oatpp::Float32>, position, "position") =
  // {{"x", 0}, {"y", 0}, {"z", 0}};
  DTO_FIELD(oatpp::postgresql::mapping::type::Point, position, "position");
  // DTO_FIELD(String, position, "position");
  DTO_FIELD(String, posegraph_id, "posegraph_id_posegraph");
};

#include OATPP_CODEGEN_END(DTO)

#endif  // POSTGRES_UTILS_VERTEXDTO_HPP
