# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: aslam/common/id.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='aslam/common/id.proto',
  package='aslam.proto',
  syntax='proto2',
  serialized_options=None,
  serialized_pb=_b('\n\x15\x61slam/common/id.proto\x12\x0b\x61slam.proto\"\x12\n\x02Id\x12\x0c\n\x04uint\x18\x01 \x03(\x04')
)




_ID = _descriptor.Descriptor(
  name='Id',
  full_name='aslam.proto.Id',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='uint', full_name='aslam.proto.Id.uint', index=0,
      number=1, type=4, cpp_type=4, label=3,
      has_default_value=False, default_value=[],
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
  serialized_start=38,
  serialized_end=56,
)

DESCRIPTOR.message_types_by_name['Id'] = _ID
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Id = _reflection.GeneratedProtocolMessageType('Id', (_message.Message,), dict(
  DESCRIPTOR = _ID,
  __module__ = 'aslam.common.id_pb2'
  # @@protoc_insertion_point(class_scope:aslam.proto.Id)
  ))
_sym_db.RegisterMessage(Id)


# @@protoc_insertion_point(module_scope)