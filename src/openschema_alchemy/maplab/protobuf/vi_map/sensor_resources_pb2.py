# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: vi-map/sensor_resources.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from maplab.protobuf.aslam.common import id_pb2 as aslam_dot_common_dot_id__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='vi-map/sensor_resources.proto',
  package='sensor_resources.proto',
  syntax='proto2',
  serialized_options=None,
  serialized_pb=_b('\n\x1dvi-map/sensor_resources.proto\x12\x16sensor_resources.proto\x1a\x15\x61slam/common/id.proto\"\x90\x01\n\x17StampedSensorResourceId\x12\"\n\tsensor_id\x18\x01 \x01(\x0b\x32\x0f.aslam.proto.Id\x12\x14\n\x0ctimestamp_ns\x18\x02 \x01(\x03\x12$\n\x0bresource_id\x18\x03 \x01(\x0b\x32\x0f.aslam.proto.Id\x12\x15\n\rresource_type\x18\x04 \x01(\x05')
  ,
  dependencies=[aslam_dot_common_dot_id__pb2.DESCRIPTOR,])




_STAMPEDSENSORRESOURCEID = _descriptor.Descriptor(
  name='StampedSensorResourceId',
  full_name='sensor_resources.proto.StampedSensorResourceId',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='sensor_id', full_name='sensor_resources.proto.StampedSensorResourceId.sensor_id', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='timestamp_ns', full_name='sensor_resources.proto.StampedSensorResourceId.timestamp_ns', index=1,
      number=2, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='resource_id', full_name='sensor_resources.proto.StampedSensorResourceId.resource_id', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='resource_type', full_name='sensor_resources.proto.StampedSensorResourceId.resource_type', index=3,
      number=4, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=81,
  serialized_end=225,
)

_STAMPEDSENSORRESOURCEID.fields_by_name['sensor_id'].message_type = aslam_dot_common_dot_id__pb2._ID
_STAMPEDSENSORRESOURCEID.fields_by_name['resource_id'].message_type = aslam_dot_common_dot_id__pb2._ID
DESCRIPTOR.message_types_by_name['StampedSensorResourceId'] = _STAMPEDSENSORRESOURCEID
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

StampedSensorResourceId = _reflection.GeneratedProtocolMessageType('StampedSensorResourceId', (_message.Message,), dict(
  DESCRIPTOR = _STAMPEDSENSORRESOURCEID,
  __module__ = 'vi_map.sensor_resources_pb2'
  # @@protoc_insertion_point(class_scope:sensor_resources.proto.StampedSensorResourceId)
  ))
_sym_db.RegisterMessage(StampedSensorResourceId)


# @@protoc_insertion_point(module_scope)
