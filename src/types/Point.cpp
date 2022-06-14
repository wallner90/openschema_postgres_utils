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

#include <ostream>

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
  // std::ostringstream stream;

  oatpp::String x(std::to_string((float)pt.x));
  oatpp::String y(std::to_string((float)pt.y));
  return {"ST_PointFromText('POINT(0 2)')"};

  // std::string point2 = std::string("POINT(0.0 0.01)");
  // return {point2};
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
  info.interpretationMap = {{"postgis", new Inter()}};
  std::cout << "ASKED FOR CLASS ID, I SAY " << Point::CLASS_ID.name
            << std::endl;
  return new oatpp::Type(Point::CLASS_ID, info);
}

oatpp::Type* Point::getType() {
  static Type* type = createType();
  return type;
}

}  // namespace __class
}  // namespace type
}  // namespace mapping
}  // namespace postgresql
}  // namespace oatpp