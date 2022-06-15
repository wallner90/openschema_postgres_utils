/***************************************************************************
 *
 * Project         _____    __   ____   _      _
 *                (  _  )  /__\ (_  _)_| |_  _| |_
 *                 )(_)(  /(__)\  )( (_   _)(_   _)
 *                (_____)(__)(__)(__)  |_|    |_|
 *
 *
 * Copyright 2018-present, Leonid Stryzhevskyi <lganzzzo@gmail.com>
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 ***************************************************************************/

#include "types/Point.hpp"

#include <oatpp/core/data/stream/BufferStream.hpp>
#include <oatpp/encoding/Unicode.hpp>
#include <ostream>
#include <sstream>

namespace oatpp {
namespace postgresql {
namespace mapping {
namespace type {

PointObject::PointObject() {}

PointObject::PointObject(v_float32 x, v_float32 y) {
  VPoint pp({x, y});
  pt = pp;
}

const VPoint PointObject::getData() const { return pt; }

v_buff_size PointObject::getSize() const { return DATA_SIZE; }

oatpp::String PointObject::toString() const {
  return {"POINT(" + std::to_string(pt.x) + " " + std::to_string(pt.y) + ")"};
  // return {"POINT(-71.060316 48.432044)"};
}

bool PointObject::operator==(const PointObject& other) const {
  return pt.x == other.pt.x and pt.y == other.pt.y;
}

bool PointObject::operator!=(const PointObject& other) const {
  return !operator==(other);
}

namespace __class {

const oatpp::ClassId Point::CLASS_ID("oatpp::postgresql::Point");

oatpp::Type* Point::createType() {
  oatpp::Type::Info info;
  info.interpretationMap = {{"postgresql", new Inter()}};

  std::cout
      << "CALLED createType(), returning type generated with CLASS_ID.name: "
      << Point::CLASS_ID.name << ", CLASS_ID.id:" << Point::CLASS_ID.id << std::endl;
  return new oatpp::Type(Point::CLASS_ID, info);
}

oatpp::Type* Point::getType() {
  static Type* type = createType();
  std::cout << "CALLED getType(), returning CLASS_ID.id: " << type->classId.id
            << " and name: " << type->classId.name << std::endl;
  return type;
}

}  // namespace __class
}  // namespace type
}  // namespace mapping
}  // namespace postgresql
}  // namespace oatpp