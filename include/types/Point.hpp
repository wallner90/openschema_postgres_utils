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

#ifndef oatpp_postgresql_mapping_type_point_hpp
#define oatpp_postgresql_mapping_type_point_hpp

#include <iostream>

#include "oatpp/core/Types.hpp"

namespace oatpp {
namespace postgresql {
namespace mapping {
namespace type {

namespace __class {
class Point;
}

struct VPoint {
  v_float32 x;
  v_float32 y;
  // v_float32 z;
};

class PointObject {
 public:
  static constexpr v_buff_size DATA_SIZE = sizeof(struct VPoint);

 private:
  VPoint pt;

 public:
  /**
   * Constructor.
   * @param text
   */
  PointObject();

  /**
   * Constructor.
   * @param data
   */
  PointObject(v_float32 x, v_float32 y);

  /**
   * Get raw data of ObjectId.
   * @return
   */
  const VPoint getData() const;

  /**
   * Get size of ObjectId data.
   * @return - &l:ObjectId::DATA_SIZE;.
   */
  v_buff_size getSize() const;

  /**
   * To hex string.
   * @return
   */
  oatpp::String toString() const;

  bool operator==(const PointObject& other) const;
  bool operator!=(const PointObject& other) const;
};

/**
 * Point type to store Point data.
 */
typedef oatpp::data::mapping::type::Primitive<PointObject, __class::Point>
    Point;

namespace __class {

class Point {
 public:
  class Inter : public oatpp::Type::Interpretation<type::Point, oatpp::String> {
   public:
    oatpp::String interpret(const type::Point& value) const override {
      std::cout << "CALLED interpret(), with Point to convert (value):  "
                << value->toString()->c_str() << std::endl;
      return value->toString();
    }

    type::Point reproduce(const oatpp::String& value) const override {
        // TODO - all of this is ugly and there most likely is a way better way
        // "pre-process" ST_asText output for POINT type to keep only coordinates
        std::string tmp(value);
        tmp.erase(tmp.find("POINT("), 6);
        tmp.erase(tmp.length()-1, 1);

        // parse remaining coordinate string
        size_t pos = 0;
        std::string token;
        std::vector<Float32> coords;
        while ((pos = tmp.find(" ")) != std::string::npos) {
            token = tmp.substr(0, pos);
            tmp.erase(0, pos + 1);
            coords.emplace_back(std::stof(token));
        }
        coords.emplace_back(std::stof(tmp));

        // create point object
        PointObject pt(coords[0], coords[1]);

        std::cout << "CALLED reproduce(), with string to parse (value):  "
                  << value->c_str() << " PARSED TO "
                  << pt.toString()->c_str() << std::endl;

        return std::make_shared<PointObject>(pt);
    }
  };

 private:
  static oatpp::Type* createType();

 public:
  static const oatpp::ClassId CLASS_ID;
  static oatpp::Type* getType();
};

}  // namespace __class

}  // namespace type
}  // namespace mapping
}  // namespace postgresql
}  // namespace oatpp

#endif  // oatpp_postgresql_mapping_type_point_hpp