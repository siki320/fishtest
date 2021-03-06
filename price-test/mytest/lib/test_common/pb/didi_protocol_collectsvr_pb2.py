# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: didi_protocol_collectsvr.proto

from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)


import didi_protocol_pb2
import didi_protocol_common_pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='didi_protocol_collectsvr.proto',
  package='DidiPush',
  serialized_pb='\n\x1e\x64idi_protocol_collectsvr.proto\x12\x08\x44idiPush\x1a\x13\x64idi_protocol.proto\x1a\x1a\x64idi_protocol_common.proto\"P\n\x04\x43ity\x12\x0e\n\x06\x63ityid\x18\x01 \x02(\r\x12\x11\n\tcity_desc\x18\x02 \x02(\t\x12\x10\n\x08\x63ountyid\x18\x03 \x02(\r\x12\x13\n\x0b\x63ounty_desc\x18\x04 \x02(\t\"[\n\x16RegulateCoordinateInfo\x12#\n\x05\x63oord\x18\x01 \x02(\x0b\x32\x14.DidiPush.Coordinate\x12\x1c\n\x14\x63ontinuous_limit_num\x18\x02 \x02(\r\"\xf1\x05\n\x17\x43ollectSvrCoordinateReq\x12\r\n\x05phone\x18\x01 \x01(\t\x12\x0b\n\x03lng\x18\x02 \x01(\x01\x12\x0b\n\x03lat\x18\x03 \x01(\x01\x12&\n\x04type\x18\x04 \x01(\x0e\x32\x18.DidiPush.CoordinateType\x12\x10\n\x08\x61\x63\x63uracy\x18\x05 \x01(\x01\x12\x11\n\tdirection\x18\x06 \x01(\x01\x12\r\n\x05speed\x18\x07 \x01(\x01\x12\x19\n\x11\x61\x63\x63\x65leratedSpeedX\x18\x08 \x01(\x02\x12\x19\n\x11\x61\x63\x63\x65leratedSpeedY\x18\t \x01(\x02\x12\x19\n\x11\x61\x63\x63\x65leratedSpeedZ\x18\n \x01(\x02\x12\x18\n\x10includedAngleYaw\x18\x0b \x01(\x02\x12\x19\n\x11includedAngleRoll\x18\x0c \x01(\x02\x12\x1a\n\x12includedAnglePitch\x18\r \x01(\x02\x12\x11\n\tpull_peer\x18\x0e \x01(\x08\x12\x0f\n\x07pre_lng\x18\x0f \x01(\x01\x12\x0f\n\x07pre_lat\x18\x10 \x01(\x01\x12\r\n\x05state\x18\x11 \x01(\r\x12\x12\n\ngps_source\x18\x12 \x01(\r\x12\x11\n\tstate_ext\x18\x13 \x01(\x05\x12\x0f\n\x07\x62iztype\x18\x14 \x01(\r\x12\x0c\n\x04role\x18\x15 \x01(\r\x12\x0f\n\x07user_id\x18\x16 \x01(\x04\x12\x11\n\tbizstatus\x18\x17 \x01(\r\x12\x13\n\x0blocate_time\x18\x18 \x01(\r\x12\x15\n\rlisten_status\x18\x19 \x01(\r\x12\x11\n\tnavi_type\x18\x1a \x01(\t\x12\x11\n\trt_status\x18\x1b \x01(\r\x12\x10\n\x08\x61ltitude\x18\x1c \x01(\x02\x12\x14\n\x0c\x61ssign_model\x18\x1d \x01(\r\x12\x14\n\x0c\x61ir_pressure\x18\x1e \x01(\x02\x12\x1c\n\x04\x63ity\x18\x1f \x01(\x0b\x32\x0e.DidiPush.City\x12\x0f\n\x07\x63\x61rpool\x18  \x01(\r\x12\x15\n\rfree_seat_num\x18! \x01(\r\x12\x16\n\x0egps_local_time\x18\" \x01(\r\x12\x13\n\x0b\x63\x61rpool_num\x18# \x01(\r\"\x88\x01\n\x18\x43ollectSvrOrderFilterReq\x12\x10\n\x08order_id\x18\x01 \x01(\t\x12\x13\n\x0b\x66ilter_type\x18\x02 \x01(\x05\x12\x11\n\tsend_info\x18\x03 \x01(\x0c\x12\x14\n\x0csub_order_id\x18\x04 \x03(\t\x12\r\n\x05phone\x18\x05 \x01(\t\x12\r\n\x05token\x18\x06 \x01(\t*~\n\x15\x43ollectSvrMessageType\x12\x31\n-kCollectSvrMessageTypeCollectSvrCoordinateReq\x10\x01\x12\x32\n.kCollectSvrMessageTypeCollectSvrOrderFilterReq\x10\x02*Z\n\tGPSSource\x12\x19\n\x15GPSSourceFromGPSModel\x10\x00\x12\x18\n\x14GPSSourceFromNetwork\x10\x01\x12\x18\n\x14GPSSourceFromUnknown\x10\x02*}\n\"DriverCollectSvrCoordinateReqState\x12\x14\n\x10\x44riverNotWorking\x10\x00\x12!\n\x1d\x44riverWorkingWithoutPassenger\x10\x01\x12\x1e\n\x1a\x44riverWorkingWithPassenger\x10\x02*h\n\x0ePassengerState\x12\x18\n\x14PassengerStateNormal\x10\x00\x12\x1c\n\x18PassengerStateHasPaidOff\x10\x01\x12\x1e\n\x1aPassengerStateHasCommented\x10\x02\x42,\n\x15\x63om.sdu.didi.protobufB\x13\x44iDiCollectProtobuf')

_COLLECTSVRMESSAGETYPE = _descriptor.EnumDescriptor(
  name='CollectSvrMessageType',
  full_name='DidiPush.CollectSvrMessageType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='kCollectSvrMessageTypeCollectSvrCoordinateReq', index=0, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='kCollectSvrMessageTypeCollectSvrOrderFilterReq', index=1, number=2,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=1163,
  serialized_end=1289,
)

CollectSvrMessageType = enum_type_wrapper.EnumTypeWrapper(_COLLECTSVRMESSAGETYPE)
_GPSSOURCE = _descriptor.EnumDescriptor(
  name='GPSSource',
  full_name='DidiPush.GPSSource',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='GPSSourceFromGPSModel', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='GPSSourceFromNetwork', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='GPSSourceFromUnknown', index=2, number=2,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=1291,
  serialized_end=1381,
)

GPSSource = enum_type_wrapper.EnumTypeWrapper(_GPSSOURCE)
_DRIVERCOLLECTSVRCOORDINATEREQSTATE = _descriptor.EnumDescriptor(
  name='DriverCollectSvrCoordinateReqState',
  full_name='DidiPush.DriverCollectSvrCoordinateReqState',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='DriverNotWorking', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DriverWorkingWithoutPassenger', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DriverWorkingWithPassenger', index=2, number=2,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=1383,
  serialized_end=1508,
)

DriverCollectSvrCoordinateReqState = enum_type_wrapper.EnumTypeWrapper(_DRIVERCOLLECTSVRCOORDINATEREQSTATE)
_PASSENGERSTATE = _descriptor.EnumDescriptor(
  name='PassengerState',
  full_name='DidiPush.PassengerState',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='PassengerStateNormal', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PassengerStateHasPaidOff', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PassengerStateHasCommented', index=2, number=2,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=1510,
  serialized_end=1614,
)

PassengerState = enum_type_wrapper.EnumTypeWrapper(_PASSENGERSTATE)
kCollectSvrMessageTypeCollectSvrCoordinateReq = 1
kCollectSvrMessageTypeCollectSvrOrderFilterReq = 2
GPSSourceFromGPSModel = 0
GPSSourceFromNetwork = 1
GPSSourceFromUnknown = 2
DriverNotWorking = 0
DriverWorkingWithoutPassenger = 1
DriverWorkingWithPassenger = 2
PassengerStateNormal = 0
PassengerStateHasPaidOff = 1
PassengerStateHasCommented = 2



_CITY = _descriptor.Descriptor(
  name='City',
  full_name='DidiPush.City',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='cityid', full_name='DidiPush.City.cityid', index=0,
      number=1, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='city_desc', full_name='DidiPush.City.city_desc', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='countyid', full_name='DidiPush.City.countyid', index=2,
      number=3, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='county_desc', full_name='DidiPush.City.county_desc', index=3,
      number=4, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=93,
  serialized_end=173,
)


_REGULATECOORDINATEINFO = _descriptor.Descriptor(
  name='RegulateCoordinateInfo',
  full_name='DidiPush.RegulateCoordinateInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='coord', full_name='DidiPush.RegulateCoordinateInfo.coord', index=0,
      number=1, type=11, cpp_type=10, label=2,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='continuous_limit_num', full_name='DidiPush.RegulateCoordinateInfo.continuous_limit_num', index=1,
      number=2, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=175,
  serialized_end=266,
)


_COLLECTSVRCOORDINATEREQ = _descriptor.Descriptor(
  name='CollectSvrCoordinateReq',
  full_name='DidiPush.CollectSvrCoordinateReq',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='phone', full_name='DidiPush.CollectSvrCoordinateReq.phone', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='lng', full_name='DidiPush.CollectSvrCoordinateReq.lng', index=1,
      number=2, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='lat', full_name='DidiPush.CollectSvrCoordinateReq.lat', index=2,
      number=3, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='type', full_name='DidiPush.CollectSvrCoordinateReq.type', index=3,
      number=4, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=1,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='accuracy', full_name='DidiPush.CollectSvrCoordinateReq.accuracy', index=4,
      number=5, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='direction', full_name='DidiPush.CollectSvrCoordinateReq.direction', index=5,
      number=6, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='speed', full_name='DidiPush.CollectSvrCoordinateReq.speed', index=6,
      number=7, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='acceleratedSpeedX', full_name='DidiPush.CollectSvrCoordinateReq.acceleratedSpeedX', index=7,
      number=8, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='acceleratedSpeedY', full_name='DidiPush.CollectSvrCoordinateReq.acceleratedSpeedY', index=8,
      number=9, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='acceleratedSpeedZ', full_name='DidiPush.CollectSvrCoordinateReq.acceleratedSpeedZ', index=9,
      number=10, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='includedAngleYaw', full_name='DidiPush.CollectSvrCoordinateReq.includedAngleYaw', index=10,
      number=11, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='includedAngleRoll', full_name='DidiPush.CollectSvrCoordinateReq.includedAngleRoll', index=11,
      number=12, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='includedAnglePitch', full_name='DidiPush.CollectSvrCoordinateReq.includedAnglePitch', index=12,
      number=13, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='pull_peer', full_name='DidiPush.CollectSvrCoordinateReq.pull_peer', index=13,
      number=14, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='pre_lng', full_name='DidiPush.CollectSvrCoordinateReq.pre_lng', index=14,
      number=15, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='pre_lat', full_name='DidiPush.CollectSvrCoordinateReq.pre_lat', index=15,
      number=16, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='state', full_name='DidiPush.CollectSvrCoordinateReq.state', index=16,
      number=17, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='gps_source', full_name='DidiPush.CollectSvrCoordinateReq.gps_source', index=17,
      number=18, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='state_ext', full_name='DidiPush.CollectSvrCoordinateReq.state_ext', index=18,
      number=19, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='biztype', full_name='DidiPush.CollectSvrCoordinateReq.biztype', index=19,
      number=20, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='role', full_name='DidiPush.CollectSvrCoordinateReq.role', index=20,
      number=21, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='user_id', full_name='DidiPush.CollectSvrCoordinateReq.user_id', index=21,
      number=22, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='bizstatus', full_name='DidiPush.CollectSvrCoordinateReq.bizstatus', index=22,
      number=23, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='locate_time', full_name='DidiPush.CollectSvrCoordinateReq.locate_time', index=23,
      number=24, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='listen_status', full_name='DidiPush.CollectSvrCoordinateReq.listen_status', index=24,
      number=25, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='navi_type', full_name='DidiPush.CollectSvrCoordinateReq.navi_type', index=25,
      number=26, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='rt_status', full_name='DidiPush.CollectSvrCoordinateReq.rt_status', index=26,
      number=27, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='altitude', full_name='DidiPush.CollectSvrCoordinateReq.altitude', index=27,
      number=28, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='assign_model', full_name='DidiPush.CollectSvrCoordinateReq.assign_model', index=28,
      number=29, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='air_pressure', full_name='DidiPush.CollectSvrCoordinateReq.air_pressure', index=29,
      number=30, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='city', full_name='DidiPush.CollectSvrCoordinateReq.city', index=30,
      number=31, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='carpool', full_name='DidiPush.CollectSvrCoordinateReq.carpool', index=31,
      number=32, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='free_seat_num', full_name='DidiPush.CollectSvrCoordinateReq.free_seat_num', index=32,
      number=33, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='gps_local_time', full_name='DidiPush.CollectSvrCoordinateReq.gps_local_time', index=33,
      number=34, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='carpool_num', full_name='DidiPush.CollectSvrCoordinateReq.carpool_num', index=34,
      number=35, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=269,
  serialized_end=1022,
)


_COLLECTSVRORDERFILTERREQ = _descriptor.Descriptor(
  name='CollectSvrOrderFilterReq',
  full_name='DidiPush.CollectSvrOrderFilterReq',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='order_id', full_name='DidiPush.CollectSvrOrderFilterReq.order_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='filter_type', full_name='DidiPush.CollectSvrOrderFilterReq.filter_type', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='send_info', full_name='DidiPush.CollectSvrOrderFilterReq.send_info', index=2,
      number=3, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value="",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='sub_order_id', full_name='DidiPush.CollectSvrOrderFilterReq.sub_order_id', index=3,
      number=4, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='phone', full_name='DidiPush.CollectSvrOrderFilterReq.phone', index=4,
      number=5, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='token', full_name='DidiPush.CollectSvrOrderFilterReq.token', index=5,
      number=6, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=1025,
  serialized_end=1161,
)

_REGULATECOORDINATEINFO.fields_by_name['coord'].message_type = didi_protocol_pb2._COORDINATE
_COLLECTSVRCOORDINATEREQ.fields_by_name['type'].enum_type = didi_protocol_pb2._COORDINATETYPE
_COLLECTSVRCOORDINATEREQ.fields_by_name['city'].message_type = _CITY
DESCRIPTOR.message_types_by_name['City'] = _CITY
DESCRIPTOR.message_types_by_name['RegulateCoordinateInfo'] = _REGULATECOORDINATEINFO
DESCRIPTOR.message_types_by_name['CollectSvrCoordinateReq'] = _COLLECTSVRCOORDINATEREQ
DESCRIPTOR.message_types_by_name['CollectSvrOrderFilterReq'] = _COLLECTSVRORDERFILTERREQ

class City(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _CITY

  # @@protoc_insertion_point(class_scope:DidiPush.City)

class RegulateCoordinateInfo(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _REGULATECOORDINATEINFO

  # @@protoc_insertion_point(class_scope:DidiPush.RegulateCoordinateInfo)

class CollectSvrCoordinateReq(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _COLLECTSVRCOORDINATEREQ

  # @@protoc_insertion_point(class_scope:DidiPush.CollectSvrCoordinateReq)

class CollectSvrOrderFilterReq(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _COLLECTSVRORDERFILTERREQ

  # @@protoc_insertion_point(class_scope:DidiPush.CollectSvrOrderFilterReq)


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), '\n\025com.sdu.didi.protobufB\023DiDiCollectProtobuf')
# @@protoc_insertion_point(module_scope)
