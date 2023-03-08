# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: aslam-serialization/visual_frame.proto

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
  name='aslam-serialization/visual_frame.proto',
  package='aslam.proto',
  syntax='proto2',
  serialized_options=None,
  serialized_pb=_b('\n&aslam-serialization/visual_frame.proto\x12\x0b\x61slam.proto\x1a\x15\x61slam/common/id.proto\"\xb9\x02\n\x0bVisualFrame\x12\x1b\n\x02id\x18\x01 \x01(\x0b\x32\x0f.aslam.proto.Id\x12\x11\n\ttimestamp\x18\x02 \x01(\x03\x12\x1d\n\x15keypoint_measurements\x18\x03 \x03(\x01\x12#\n\x1bkeypoint_measurement_sigmas\x18\x04 \x03(\x01\x12\x1c\n\x14keypoint_descriptors\x18\x05 \x01(\x0c\x12 \n\x18keypoint_descriptor_size\x18\x06 \x01(\r\x12%\n\x0clandmark_ids\x18\x07 \x03(\x0b\x32\x0f.aslam.proto.Id\x12\x19\n\x11\x64\x65scriptor_scales\x18\x08 \x03(\x01\x12\x10\n\x08is_valid\x18\t \x01(\x08\x12\x11\n\ttrack_ids\x18\n \x03(\x05\x12\x0f\n\x07tag_ids\x18\x0b \x03(\x01\"U\n\x0cVisualNFrame\x12\x1b\n\x02id\x18\x01 \x01(\x0b\x32\x0f.aslam.proto.Id\x12(\n\x06\x66rames\x18\x02 \x03(\x0b\x32\x18.aslam.proto.VisualFrame')
  ,
  dependencies=[aslam_dot_common_dot_id__pb2.DESCRIPTOR,])




_VISUALFRAME = _descriptor.Descriptor(
  name='VisualFrame',
  full_name='aslam.proto.VisualFrame',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='aslam.proto.VisualFrame.id', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='timestamp', full_name='aslam.proto.VisualFrame.timestamp', index=1,
      number=2, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='keypoint_measurements', full_name='aslam.proto.VisualFrame.keypoint_measurements', index=2,
      number=3, type=1, cpp_type=5, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='keypoint_measurement_sigmas', full_name='aslam.proto.VisualFrame.keypoint_measurement_sigmas', index=3,
      number=4, type=1, cpp_type=5, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='keypoint_descriptors', full_name='aslam.proto.VisualFrame.keypoint_descriptors', index=4,
      number=5, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='keypoint_descriptor_size', full_name='aslam.proto.VisualFrame.keypoint_descriptor_size', index=5,
      number=6, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='landmark_ids', full_name='aslam.proto.VisualFrame.landmark_ids', index=6,
      number=7, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='descriptor_scales', full_name='aslam.proto.VisualFrame.descriptor_scales', index=7,
      number=8, type=1, cpp_type=5, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='is_valid', full_name='aslam.proto.VisualFrame.is_valid', index=8,
      number=9, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='track_ids', full_name='aslam.proto.VisualFrame.track_ids', index=9,
      number=10, type=5, cpp_type=1, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='tag_ids', full_name='aslam.proto.VisualFrame.tag_ids', index=10,
      number=11, type=1, cpp_type=5, label=3,
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
  serialized_start=79,
  serialized_end=392,
)


_VISUALNFRAME = _descriptor.Descriptor(
  name='VisualNFrame',
  full_name='aslam.proto.VisualNFrame',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='aslam.proto.VisualNFrame.id', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='frames', full_name='aslam.proto.VisualNFrame.frames', index=1,
      number=2, type=11, cpp_type=10, label=3,
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
  serialized_start=394,
  serialized_end=479,
)

_VISUALFRAME.fields_by_name['id'].message_type = aslam_dot_common_dot_id__pb2._ID
_VISUALFRAME.fields_by_name['landmark_ids'].message_type = aslam_dot_common_dot_id__pb2._ID
_VISUALNFRAME.fields_by_name['id'].message_type = aslam_dot_common_dot_id__pb2._ID
_VISUALNFRAME.fields_by_name['frames'].message_type = _VISUALFRAME
DESCRIPTOR.message_types_by_name['VisualFrame'] = _VISUALFRAME
DESCRIPTOR.message_types_by_name['VisualNFrame'] = _VISUALNFRAME
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

VisualFrame = _reflection.GeneratedProtocolMessageType('VisualFrame', (_message.Message,), dict(
  DESCRIPTOR = _VISUALFRAME,
  __module__ = 'aslam_serialization.visual_frame_pb2'
  # @@protoc_insertion_point(class_scope:aslam.proto.VisualFrame)
  ))
_sym_db.RegisterMessage(VisualFrame)

VisualNFrame = _reflection.GeneratedProtocolMessageType('VisualNFrame', (_message.Message,), dict(
  DESCRIPTOR = _VISUALNFRAME,
  __module__ = 'aslam_serialization.visual_frame_pb2'
  # @@protoc_insertion_point(class_scope:aslam.proto.VisualNFrame)
  ))
_sym_db.RegisterMessage(VisualNFrame)


# @@protoc_insertion_point(module_scope)