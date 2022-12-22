# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: aslam-serialization/camera.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from maplab.vimap.proto.aslam.common import id_pb2 as aslam_dot_common_dot_id__pb2
from maplab.vimap.proto.maplab_common import eigen_pb2 as maplab__common_dot_eigen__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='aslam-serialization/camera.proto',
  package='aslam.proto',
  syntax='proto2',
  serialized_options=None,
  serialized_pb=_b('\n aslam-serialization/camera.proto\x12\x0b\x61slam.proto\x1a\x15\x61slam/common/id.proto\x1a\x19maplab-common/eigen.proto\"\x9f\x03\n\x06\x43\x61mera\x12\x1b\n\x02id\x18\x01 \x01(\x0b\x32\x0f.aslam.proto.Id\x12\x33\n\x0b\x63\x61mera_type\x18\x02 \x01(\x0e\x32\x1e.aslam.proto.Camera.CameraType\x12\x12\n\nintrinsics\x18\x03 \x03(\x01\x12\x14\n\x0cimage_height\x18\x04 \x01(\r\x12\x13\n\x0bimage_width\x18\x05 \x01(\r\x12;\n\x0f\x64istortion_type\x18\x06 \x01(\x0e\x32\".aslam.proto.Camera.DistortionType\x12\x1d\n\x15\x64istortion_parameters\x18\x07 \x03(\x01\x12\r\n\x05topic\x18\x08 \x01(\t\x12\x13\n\x0b\x64\x65scription\x18\t \x01(\t\"2\n\nCameraType\x12\x0c\n\x08kPinhole\x10\x00\x12\x16\n\x12kUnifiedProjection\x10\x01\"P\n\x0e\x44istortionType\x12\x11\n\rkNoDistortion\x10\x00\x12\x10\n\x0ckEquidistant\x10\x01\x12\x0c\n\x08kFisheye\x10\x02\x12\x0b\n\x07kRadTan\x10\x03\"\xab\x01\n\x07NCamera\x12\x1b\n\x02id\x18\x01 \x01(\x0b\x32\x0f.aslam.proto.Id\x12\r\n\x05topic\x18\x02 \x01(\t\x12\x13\n\x0b\x64\x65scription\x18\x03 \x01(\t\x12$\n\x07\x63\x61meras\x18\x04 \x03(\x0b\x32\x13.aslam.proto.Camera\x12\x39\n\x10T_C_I_transforms\x18\x05 \x03(\x0b\x32\x1f.common.proto.SemiStaticMatrixd')
  ,
  dependencies=[aslam_dot_common_dot_id__pb2.DESCRIPTOR,maplab__common_dot_eigen__pb2.DESCRIPTOR,])



_CAMERA_CAMERATYPE = _descriptor.EnumDescriptor(
  name='CameraType',
  full_name='aslam.proto.Camera.CameraType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='kPinhole', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='kUnifiedProjection', index=1, number=1,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=383,
  serialized_end=433,
)
_sym_db.RegisterEnumDescriptor(_CAMERA_CAMERATYPE)

_CAMERA_DISTORTIONTYPE = _descriptor.EnumDescriptor(
  name='DistortionType',
  full_name='aslam.proto.Camera.DistortionType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='kNoDistortion', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='kEquidistant', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='kFisheye', index=2, number=2,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='kRadTan', index=3, number=3,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=435,
  serialized_end=515,
)
_sym_db.RegisterEnumDescriptor(_CAMERA_DISTORTIONTYPE)


_CAMERA = _descriptor.Descriptor(
  name='Camera',
  full_name='aslam.proto.Camera',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='aslam.proto.Camera.id', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='camera_type', full_name='aslam.proto.Camera.camera_type', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='intrinsics', full_name='aslam.proto.Camera.intrinsics', index=2,
      number=3, type=1, cpp_type=5, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='image_height', full_name='aslam.proto.Camera.image_height', index=3,
      number=4, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='image_width', full_name='aslam.proto.Camera.image_width', index=4,
      number=5, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='distortion_type', full_name='aslam.proto.Camera.distortion_type', index=5,
      number=6, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='distortion_parameters', full_name='aslam.proto.Camera.distortion_parameters', index=6,
      number=7, type=1, cpp_type=5, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='topic', full_name='aslam.proto.Camera.topic', index=7,
      number=8, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='description', full_name='aslam.proto.Camera.description', index=8,
      number=9, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _CAMERA_CAMERATYPE,
    _CAMERA_DISTORTIONTYPE,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=100,
  serialized_end=515,
)


_NCAMERA = _descriptor.Descriptor(
  name='NCamera',
  full_name='aslam.proto.NCamera',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='aslam.proto.NCamera.id', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='topic', full_name='aslam.proto.NCamera.topic', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='description', full_name='aslam.proto.NCamera.description', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='cameras', full_name='aslam.proto.NCamera.cameras', index=3,
      number=4, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='T_C_I_transforms', full_name='aslam.proto.NCamera.T_C_I_transforms', index=4,
      number=5, type=11, cpp_type=10, label=3,
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
  serialized_start=518,
  serialized_end=689,
)

_CAMERA.fields_by_name['id'].message_type = aslam_dot_common_dot_id__pb2._ID
_CAMERA.fields_by_name['camera_type'].enum_type = _CAMERA_CAMERATYPE
_CAMERA.fields_by_name['distortion_type'].enum_type = _CAMERA_DISTORTIONTYPE
_CAMERA_CAMERATYPE.containing_type = _CAMERA
_CAMERA_DISTORTIONTYPE.containing_type = _CAMERA
_NCAMERA.fields_by_name['id'].message_type = aslam_dot_common_dot_id__pb2._ID
_NCAMERA.fields_by_name['cameras'].message_type = _CAMERA
_NCAMERA.fields_by_name['T_C_I_transforms'].message_type = maplab__common_dot_eigen__pb2._SEMISTATICMATRIXD
DESCRIPTOR.message_types_by_name['Camera'] = _CAMERA
DESCRIPTOR.message_types_by_name['NCamera'] = _NCAMERA
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Camera = _reflection.GeneratedProtocolMessageType('Camera', (_message.Message,), dict(
  DESCRIPTOR = _CAMERA,
  __module__ = 'aslam_serialization.camera_pb2'
  # @@protoc_insertion_point(class_scope:aslam.proto.Camera)
  ))
_sym_db.RegisterMessage(Camera)

NCamera = _reflection.GeneratedProtocolMessageType('NCamera', (_message.Message,), dict(
  DESCRIPTOR = _NCAMERA,
  __module__ = 'aslam_serialization.camera_pb2'
  # @@protoc_insertion_point(class_scope:aslam.proto.NCamera)
  ))
_sym_db.RegisterMessage(NCamera)


# @@protoc_insertion_point(module_scope)
