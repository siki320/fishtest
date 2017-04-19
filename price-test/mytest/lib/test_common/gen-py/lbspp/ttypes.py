#
# Autogenerated by Thrift Compiler (0.9.2)
#
# DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
#
#  options string: py
#

from thrift.Thrift import TType, TMessageType, TException, TApplicationException

from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol, TProtocol
try:
  from thrift.protocol import fastbinary
except:
  fastbinary = None


class Error:
  INVALID_TRANS_ID = 1
  INVALID_SERVICE_TYPE = 2
  INVALID_COORD_TYPE = 3
  INVALID_FRAG = 4
  INVALID_COORD = 5
  INVALID_COUNT = 6
  INVALID_RADIUS = 7
  NO_RESULT = 8
  SERVER_ERROR = 9
  CLIENT_INVALID_ARGUMENT = 10
  INVALID_POINT_SEARCH_TYPE = 11

  _VALUES_TO_NAMES = {
    1: "INVALID_TRANS_ID",
    2: "INVALID_SERVICE_TYPE",
    3: "INVALID_COORD_TYPE",
    4: "INVALID_FRAG",
    5: "INVALID_COORD",
    6: "INVALID_COUNT",
    7: "INVALID_RADIUS",
    8: "NO_RESULT",
    9: "SERVER_ERROR",
    10: "CLIENT_INVALID_ARGUMENT",
    11: "INVALID_POINT_SEARCH_TYPE",
  }

  _NAMES_TO_VALUES = {
    "INVALID_TRANS_ID": 1,
    "INVALID_SERVICE_TYPE": 2,
    "INVALID_COORD_TYPE": 3,
    "INVALID_FRAG": 4,
    "INVALID_COORD": 5,
    "INVALID_COUNT": 6,
    "INVALID_RADIUS": 7,
    "NO_RESULT": 8,
    "SERVER_ERROR": 9,
    "CLIENT_INVALID_ARGUMENT": 10,
    "INVALID_POINT_SEARCH_TYPE": 11,
  }

class CoordType:
  BAIDU = 1
  SOSOGCJ = 2
  WGS84 = 3

  _VALUES_TO_NAMES = {
    1: "BAIDU",
    2: "SOSOGCJ",
    3: "WGS84",
  }

  _NAMES_TO_VALUES = {
    "BAIDU": 1,
    "SOSOGCJ": 2,
    "WGS84": 3,
  }

class SearchMode:
  ACCUR = 1
  INACCUR = 2

  _VALUES_TO_NAMES = {
    1: "ACCUR",
    2: "INACCUR",
  }

  _NAMES_TO_VALUES = {
    "ACCUR": 1,
    "INACCUR": 2,
  }

class ValueOperator:
  EQUAL = 1
  NOT_EQUAL = 2
  LESS = 3
  LARGER = 4

  _VALUES_TO_NAMES = {
    1: "EQUAL",
    2: "NOT_EQUAL",
    3: "LESS",
    4: "LARGER",
  }

  _NAMES_TO_VALUES = {
    "EQUAL": 1,
    "NOT_EQUAL": 2,
    "LESS": 3,
    "LARGER": 4,
  }

class SetOperator:
  IN = 1
  NOT_IN = 2

  _VALUES_TO_NAMES = {
    1: "IN",
    2: "NOT_IN",
  }

  _NAMES_TO_VALUES = {
    "IN": 1,
    "NOT_IN": 2,
  }


class RespMsg:
  """
  Attributes:
   - errcode
   - errmsg
   - details
  """

  thrift_spec = (
    None, # 0
    (1, TType.I64, 'errcode', None, None, ), # 1
    (2, TType.STRING, 'errmsg', None, None, ), # 2
    (3, TType.MAP, 'details', (TType.STRING,None,TType.STRING,None), None, ), # 3
  )

  def __init__(self, errcode=None, errmsg=None, details=None,):
    self.errcode = errcode
    self.errmsg = errmsg
    self.details = details

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.I64:
          self.errcode = iprot.readI64();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRING:
          self.errmsg = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.MAP:
          self.details = {}
          (_ktype1, _vtype2, _size0 ) = iprot.readMapBegin()
          for _i4 in xrange(_size0):
            _key5 = iprot.readString();
            _val6 = iprot.readString();
            self.details[_key5] = _val6
          iprot.readMapEnd()
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('RespMsg')
    if self.errcode is not None:
      oprot.writeFieldBegin('errcode', TType.I64, 1)
      oprot.writeI64(self.errcode)
      oprot.writeFieldEnd()
    if self.errmsg is not None:
      oprot.writeFieldBegin('errmsg', TType.STRING, 2)
      oprot.writeString(self.errmsg)
      oprot.writeFieldEnd()
    if self.details is not None:
      oprot.writeFieldBegin('details', TType.MAP, 3)
      oprot.writeMapBegin(TType.STRING, TType.STRING, len(self.details))
      for kiter7,viter8 in self.details.items():
        oprot.writeString(kiter7)
        oprot.writeString(viter8)
      oprot.writeMapEnd()
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __hash__(self):
    value = 17
    value = (value * 31) ^ hash(self.errcode)
    value = (value * 31) ^ hash(self.errmsg)
    value = (value * 31) ^ hash(self.details)
    return value

  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class LbsppException(TException):
  """
  Attributes:
   - errcode
   - errmsg
   - details
  """

  thrift_spec = (
    None, # 0
    (1, TType.I64, 'errcode', None, None, ), # 1
    (2, TType.STRING, 'errmsg', None, None, ), # 2
    (3, TType.MAP, 'details', (TType.STRING,None,TType.STRING,None), None, ), # 3
  )

  def __init__(self, errcode=None, errmsg=None, details=None,):
    self.errcode = errcode
    self.errmsg = errmsg
    self.details = details

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.I64:
          self.errcode = iprot.readI64();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRING:
          self.errmsg = iprot.readString();
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.MAP:
          self.details = {}
          (_ktype10, _vtype11, _size9 ) = iprot.readMapBegin()
          for _i13 in xrange(_size9):
            _key14 = iprot.readString();
            _val15 = iprot.readString();
            self.details[_key14] = _val15
          iprot.readMapEnd()
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('LbsppException')
    if self.errcode is not None:
      oprot.writeFieldBegin('errcode', TType.I64, 1)
      oprot.writeI64(self.errcode)
      oprot.writeFieldEnd()
    if self.errmsg is not None:
      oprot.writeFieldBegin('errmsg', TType.STRING, 2)
      oprot.writeString(self.errmsg)
      oprot.writeFieldEnd()
    if self.details is not None:
      oprot.writeFieldBegin('details', TType.MAP, 3)
      oprot.writeMapBegin(TType.STRING, TType.STRING, len(self.details))
      for kiter16,viter17 in self.details.items():
        oprot.writeString(kiter16)
        oprot.writeString(viter17)
      oprot.writeMapEnd()
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __str__(self):
    return repr(self)

  def __hash__(self):
    value = 17
    value = (value * 31) ^ hash(self.errcode)
    value = (value * 31) ^ hash(self.errmsg)
    value = (value * 31) ^ hash(self.details)
    return value

  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class ValueFilter:
  """
  Attributes:
   - oper
   - value
  """

  thrift_spec = (
    None, # 0
    (1, TType.I32, 'oper', None, None, ), # 1
    (2, TType.I64, 'value', None, None, ), # 2
  )

  def __init__(self, oper=None, value=None,):
    self.oper = oper
    self.value = value

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.I32:
          self.oper = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.I64:
          self.value = iprot.readI64();
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('ValueFilter')
    if self.oper is not None:
      oprot.writeFieldBegin('oper', TType.I32, 1)
      oprot.writeI32(self.oper)
      oprot.writeFieldEnd()
    if self.value is not None:
      oprot.writeFieldBegin('value', TType.I64, 2)
      oprot.writeI64(self.value)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __hash__(self):
    value = 17
    value = (value * 31) ^ hash(self.oper)
    value = (value * 31) ^ hash(self.value)
    return value

  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class SetFilter:
  """
  Attributes:
   - oper
   - values
  """

  thrift_spec = (
    None, # 0
    (1, TType.I32, 'oper', None, None, ), # 1
    (2, TType.SET, 'values', (TType.I64,None), None, ), # 2
  )

  def __init__(self, oper=None, values=None,):
    self.oper = oper
    self.values = values

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.I32:
          self.oper = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.SET:
          self.values = set()
          (_etype21, _size18) = iprot.readSetBegin()
          for _i22 in xrange(_size18):
            _elem23 = iprot.readI64();
            self.values.add(_elem23)
          iprot.readSetEnd()
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('SetFilter')
    if self.oper is not None:
      oprot.writeFieldBegin('oper', TType.I32, 1)
      oprot.writeI32(self.oper)
      oprot.writeFieldEnd()
    if self.values is not None:
      oprot.writeFieldBegin('values', TType.SET, 2)
      oprot.writeSetBegin(TType.I64, len(self.values))
      for iter24 in self.values:
        oprot.writeI64(iter24)
      oprot.writeSetEnd()
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __hash__(self):
    value = 17
    value = (value * 31) ^ hash(self.oper)
    value = (value * 31) ^ hash(self.values)
    return value

  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class SearchFilter:
  """
  Attributes:
   - mode
   - bmfilter
   - vfilter
   - setfilter
  """

  thrift_spec = (
    None, # 0
    (1, TType.I32, 'mode', None, None, ), # 1
    (2, TType.MAP, 'bmfilter', (TType.STRING,None,TType.I64,None), None, ), # 2
    (3, TType.MAP, 'vfilter', (TType.STRING,None,TType.LIST,(TType.STRUCT,(ValueFilter, ValueFilter.thrift_spec))), None, ), # 3
    (4, TType.MAP, 'setfilter', (TType.STRING,None,TType.STRUCT,(SetFilter, SetFilter.thrift_spec)), None, ), # 4
  )

  def __init__(self, mode=None, bmfilter=None, vfilter=None, setfilter=None,):
    self.mode = mode
    self.bmfilter = bmfilter
    self.vfilter = vfilter
    self.setfilter = setfilter

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.I32:
          self.mode = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.MAP:
          self.bmfilter = {}
          (_ktype26, _vtype27, _size25 ) = iprot.readMapBegin()
          for _i29 in xrange(_size25):
            _key30 = iprot.readString();
            _val31 = iprot.readI64();
            self.bmfilter[_key30] = _val31
          iprot.readMapEnd()
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.MAP:
          self.vfilter = {}
          (_ktype33, _vtype34, _size32 ) = iprot.readMapBegin()
          for _i36 in xrange(_size32):
            _key37 = iprot.readString();
            _val38 = []
            (_etype42, _size39) = iprot.readListBegin()
            for _i43 in xrange(_size39):
              _elem44 = ValueFilter()
              _elem44.read(iprot)
              _val38.append(_elem44)
            iprot.readListEnd()
            self.vfilter[_key37] = _val38
          iprot.readMapEnd()
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.MAP:
          self.setfilter = {}
          (_ktype46, _vtype47, _size45 ) = iprot.readMapBegin()
          for _i49 in xrange(_size45):
            _key50 = iprot.readString();
            _val51 = SetFilter()
            _val51.read(iprot)
            self.setfilter[_key50] = _val51
          iprot.readMapEnd()
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('SearchFilter')
    if self.mode is not None:
      oprot.writeFieldBegin('mode', TType.I32, 1)
      oprot.writeI32(self.mode)
      oprot.writeFieldEnd()
    if self.bmfilter is not None:
      oprot.writeFieldBegin('bmfilter', TType.MAP, 2)
      oprot.writeMapBegin(TType.STRING, TType.I64, len(self.bmfilter))
      for kiter52,viter53 in self.bmfilter.items():
        oprot.writeString(kiter52)
        oprot.writeI64(viter53)
      oprot.writeMapEnd()
      oprot.writeFieldEnd()
    if self.vfilter is not None:
      oprot.writeFieldBegin('vfilter', TType.MAP, 3)
      oprot.writeMapBegin(TType.STRING, TType.LIST, len(self.vfilter))
      for kiter54,viter55 in self.vfilter.items():
        oprot.writeString(kiter54)
        oprot.writeListBegin(TType.STRUCT, len(viter55))
        for iter56 in viter55:
          iter56.write(oprot)
        oprot.writeListEnd()
      oprot.writeMapEnd()
      oprot.writeFieldEnd()
    if self.setfilter is not None:
      oprot.writeFieldBegin('setfilter', TType.MAP, 4)
      oprot.writeMapBegin(TType.STRING, TType.STRUCT, len(self.setfilter))
      for kiter57,viter58 in self.setfilter.items():
        oprot.writeString(kiter57)
        viter58.write(oprot)
      oprot.writeMapEnd()
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __hash__(self):
    value = 17
    value = (value * 31) ^ hash(self.mode)
    value = (value * 31) ^ hash(self.bmfilter)
    value = (value * 31) ^ hash(self.vfilter)
    value = (value * 31) ^ hash(self.setfilter)
    return value

  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class Business:
  """
  Attributes:
   - id
   - type
  """

  thrift_spec = (
    None, # 0
    (1, TType.I64, 'id', None, None, ), # 1
    (2, TType.I64, 'type', None, None, ), # 2
  )

  def __init__(self, id=None, type=None,):
    self.id = id
    self.type = type

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.I64:
          self.id = iprot.readI64();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.I64:
          self.type = iprot.readI64();
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('Business')
    if self.id is not None:
      oprot.writeFieldBegin('id', TType.I64, 1)
      oprot.writeI64(self.id)
      oprot.writeFieldEnd()
    if self.type is not None:
      oprot.writeFieldBegin('type', TType.I64, 2)
      oprot.writeI64(self.type)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __hash__(self):
    value = 17
    value = (value * 31) ^ hash(self.id)
    value = (value * 31) ^ hash(self.type)
    return value

  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class Coordinate:
  """
  Attributes:
   - lng
   - lat
   - coord_type
   - timestamp
   - accuracy
   - gps_source
   - angle
   - distance
   - speed
   - altitude
  """

  thrift_spec = (
    None, # 0
    (1, TType.DOUBLE, 'lng', None, None, ), # 1
    (2, TType.DOUBLE, 'lat', None, None, ), # 2
    (3, TType.I32, 'coord_type', None, None, ), # 3
    (4, TType.I64, 'timestamp', None, None, ), # 4
    (5, TType.DOUBLE, 'accuracy', None, None, ), # 5
    (6, TType.I64, 'gps_source', None, None, ), # 6
    (7, TType.I64, 'angle', None, None, ), # 7
    (8, TType.DOUBLE, 'distance', None, None, ), # 8
    (9, TType.DOUBLE, 'speed', None, None, ), # 9
    (10, TType.DOUBLE, 'altitude', None, None, ), # 10
  )

  def __init__(self, lng=None, lat=None, coord_type=None, timestamp=None, accuracy=None, gps_source=None, angle=None, distance=None, speed=None, altitude=None,):
    self.lng = lng
    self.lat = lat
    self.coord_type = coord_type
    self.timestamp = timestamp
    self.accuracy = accuracy
    self.gps_source = gps_source
    self.angle = angle
    self.distance = distance
    self.speed = speed
    self.altitude = altitude

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.DOUBLE:
          self.lng = iprot.readDouble();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.DOUBLE:
          self.lat = iprot.readDouble();
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.I32:
          self.coord_type = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.I64:
          self.timestamp = iprot.readI64();
        else:
          iprot.skip(ftype)
      elif fid == 5:
        if ftype == TType.DOUBLE:
          self.accuracy = iprot.readDouble();
        else:
          iprot.skip(ftype)
      elif fid == 6:
        if ftype == TType.I64:
          self.gps_source = iprot.readI64();
        else:
          iprot.skip(ftype)
      elif fid == 7:
        if ftype == TType.I64:
          self.angle = iprot.readI64();
        else:
          iprot.skip(ftype)
      elif fid == 8:
        if ftype == TType.DOUBLE:
          self.distance = iprot.readDouble();
        else:
          iprot.skip(ftype)
      elif fid == 9:
        if ftype == TType.DOUBLE:
          self.speed = iprot.readDouble();
        else:
          iprot.skip(ftype)
      elif fid == 10:
        if ftype == TType.DOUBLE:
          self.altitude = iprot.readDouble();
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('Coordinate')
    if self.lng is not None:
      oprot.writeFieldBegin('lng', TType.DOUBLE, 1)
      oprot.writeDouble(self.lng)
      oprot.writeFieldEnd()
    if self.lat is not None:
      oprot.writeFieldBegin('lat', TType.DOUBLE, 2)
      oprot.writeDouble(self.lat)
      oprot.writeFieldEnd()
    if self.coord_type is not None:
      oprot.writeFieldBegin('coord_type', TType.I32, 3)
      oprot.writeI32(self.coord_type)
      oprot.writeFieldEnd()
    if self.timestamp is not None:
      oprot.writeFieldBegin('timestamp', TType.I64, 4)
      oprot.writeI64(self.timestamp)
      oprot.writeFieldEnd()
    if self.accuracy is not None:
      oprot.writeFieldBegin('accuracy', TType.DOUBLE, 5)
      oprot.writeDouble(self.accuracy)
      oprot.writeFieldEnd()
    if self.gps_source is not None:
      oprot.writeFieldBegin('gps_source', TType.I64, 6)
      oprot.writeI64(self.gps_source)
      oprot.writeFieldEnd()
    if self.angle is not None:
      oprot.writeFieldBegin('angle', TType.I64, 7)
      oprot.writeI64(self.angle)
      oprot.writeFieldEnd()
    if self.distance is not None:
      oprot.writeFieldBegin('distance', TType.DOUBLE, 8)
      oprot.writeDouble(self.distance)
      oprot.writeFieldEnd()
    if self.speed is not None:
      oprot.writeFieldBegin('speed', TType.DOUBLE, 9)
      oprot.writeDouble(self.speed)
      oprot.writeFieldEnd()
    if self.altitude is not None:
      oprot.writeFieldBegin('altitude', TType.DOUBLE, 10)
      oprot.writeDouble(self.altitude)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __hash__(self):
    value = 17
    value = (value * 31) ^ hash(self.lng)
    value = (value * 31) ^ hash(self.lat)
    value = (value * 31) ^ hash(self.coord_type)
    value = (value * 31) ^ hash(self.timestamp)
    value = (value * 31) ^ hash(self.accuracy)
    value = (value * 31) ^ hash(self.gps_source)
    value = (value * 31) ^ hash(self.angle)
    value = (value * 31) ^ hash(self.distance)
    value = (value * 31) ^ hash(self.speed)
    value = (value * 31) ^ hash(self.altitude)
    return value

  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class CoordinateBean:
  """
  Attributes:
   - id
   - biz
   - coord_info
   - status_info
  """

  thrift_spec = (
    None, # 0
    (1, TType.I64, 'id', None, None, ), # 1
    (2, TType.STRUCT, 'biz', (Business, Business.thrift_spec), None, ), # 2
    (3, TType.STRUCT, 'coord_info', (Coordinate, Coordinate.thrift_spec), None, ), # 3
    (4, TType.MAP, 'status_info', (TType.STRING,None,TType.I64,None), None, ), # 4
  )

  def __init__(self, id=None, biz=None, coord_info=None, status_info=None,):
    self.id = id
    self.biz = biz
    self.coord_info = coord_info
    self.status_info = status_info

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.I64:
          self.id = iprot.readI64();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRUCT:
          self.biz = Business()
          self.biz.read(iprot)
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.STRUCT:
          self.coord_info = Coordinate()
          self.coord_info.read(iprot)
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.MAP:
          self.status_info = {}
          (_ktype60, _vtype61, _size59 ) = iprot.readMapBegin()
          for _i63 in xrange(_size59):
            _key64 = iprot.readString();
            _val65 = iprot.readI64();
            self.status_info[_key64] = _val65
          iprot.readMapEnd()
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('CoordinateBean')
    if self.id is not None:
      oprot.writeFieldBegin('id', TType.I64, 1)
      oprot.writeI64(self.id)
      oprot.writeFieldEnd()
    if self.biz is not None:
      oprot.writeFieldBegin('biz', TType.STRUCT, 2)
      self.biz.write(oprot)
      oprot.writeFieldEnd()
    if self.coord_info is not None:
      oprot.writeFieldBegin('coord_info', TType.STRUCT, 3)
      self.coord_info.write(oprot)
      oprot.writeFieldEnd()
    if self.status_info is not None:
      oprot.writeFieldBegin('status_info', TType.MAP, 4)
      oprot.writeMapBegin(TType.STRING, TType.I64, len(self.status_info))
      for kiter66,viter67 in self.status_info.items():
        oprot.writeString(kiter66)
        oprot.writeI64(viter67)
      oprot.writeMapEnd()
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __hash__(self):
    value = 17
    value = (value * 31) ^ hash(self.id)
    value = (value * 31) ^ hash(self.biz)
    value = (value * 31) ^ hash(self.coord_info)
    value = (value * 31) ^ hash(self.status_info)
    return value

  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class Area:
  """
  Attributes:
   - coord_type
   - lng
   - lat
   - radius
   - output_coord_type
  """

  thrift_spec = (
    None, # 0
    (1, TType.I32, 'coord_type', None, None, ), # 1
    (2, TType.DOUBLE, 'lng', None, None, ), # 2
    (3, TType.DOUBLE, 'lat', None, None, ), # 3
    (4, TType.DOUBLE, 'radius', None, None, ), # 4
    (5, TType.I32, 'output_coord_type', None, None, ), # 5
  )

  def __init__(self, coord_type=None, lng=None, lat=None, radius=None, output_coord_type=None,):
    self.coord_type = coord_type
    self.lng = lng
    self.lat = lat
    self.radius = radius
    self.output_coord_type = output_coord_type

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.I32:
          self.coord_type = iprot.readI32();
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.DOUBLE:
          self.lng = iprot.readDouble();
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.DOUBLE:
          self.lat = iprot.readDouble();
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.DOUBLE:
          self.radius = iprot.readDouble();
        else:
          iprot.skip(ftype)
      elif fid == 5:
        if ftype == TType.I32:
          self.output_coord_type = iprot.readI32();
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('Area')
    if self.coord_type is not None:
      oprot.writeFieldBegin('coord_type', TType.I32, 1)
      oprot.writeI32(self.coord_type)
      oprot.writeFieldEnd()
    if self.lng is not None:
      oprot.writeFieldBegin('lng', TType.DOUBLE, 2)
      oprot.writeDouble(self.lng)
      oprot.writeFieldEnd()
    if self.lat is not None:
      oprot.writeFieldBegin('lat', TType.DOUBLE, 3)
      oprot.writeDouble(self.lat)
      oprot.writeFieldEnd()
    if self.radius is not None:
      oprot.writeFieldBegin('radius', TType.DOUBLE, 4)
      oprot.writeDouble(self.radius)
      oprot.writeFieldEnd()
    if self.output_coord_type is not None:
      oprot.writeFieldBegin('output_coord_type', TType.I32, 5)
      oprot.writeI32(self.output_coord_type)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __hash__(self):
    value = 17
    value = (value * 31) ^ hash(self.coord_type)
    value = (value * 31) ^ hash(self.lng)
    value = (value * 31) ^ hash(self.lat)
    value = (value * 31) ^ hash(self.radius)
    value = (value * 31) ^ hash(self.output_coord_type)
    return value

  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)

class BizSearchPara:
  """
  Attributes:
   - biz
   - area
   - seconds
   - search_filter
  """

  thrift_spec = (
    None, # 0
    (1, TType.STRUCT, 'biz', (Business, Business.thrift_spec), None, ), # 1
    (2, TType.STRUCT, 'area', (Area, Area.thrift_spec), None, ), # 2
    (3, TType.I64, 'seconds', None, None, ), # 3
    (4, TType.STRUCT, 'search_filter', (SearchFilter, SearchFilter.thrift_spec), None, ), # 4
  )

  def __init__(self, biz=None, area=None, seconds=None, search_filter=None,):
    self.biz = biz
    self.area = area
    self.seconds = seconds
    self.search_filter = search_filter

  def read(self, iprot):
    if iprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and isinstance(iprot.trans, TTransport.CReadableTransport) and self.thrift_spec is not None and fastbinary is not None:
      fastbinary.decode_binary(self, iprot.trans, (self.__class__, self.thrift_spec))
      return
    iprot.readStructBegin()
    while True:
      (fname, ftype, fid) = iprot.readFieldBegin()
      if ftype == TType.STOP:
        break
      if fid == 1:
        if ftype == TType.STRUCT:
          self.biz = Business()
          self.biz.read(iprot)
        else:
          iprot.skip(ftype)
      elif fid == 2:
        if ftype == TType.STRUCT:
          self.area = Area()
          self.area.read(iprot)
        else:
          iprot.skip(ftype)
      elif fid == 3:
        if ftype == TType.I64:
          self.seconds = iprot.readI64();
        else:
          iprot.skip(ftype)
      elif fid == 4:
        if ftype == TType.STRUCT:
          self.search_filter = SearchFilter()
          self.search_filter.read(iprot)
        else:
          iprot.skip(ftype)
      else:
        iprot.skip(ftype)
      iprot.readFieldEnd()
    iprot.readStructEnd()

  def write(self, oprot):
    if oprot.__class__ == TBinaryProtocol.TBinaryProtocolAccelerated and self.thrift_spec is not None and fastbinary is not None:
      oprot.trans.write(fastbinary.encode_binary(self, (self.__class__, self.thrift_spec)))
      return
    oprot.writeStructBegin('BizSearchPara')
    if self.biz is not None:
      oprot.writeFieldBegin('biz', TType.STRUCT, 1)
      self.biz.write(oprot)
      oprot.writeFieldEnd()
    if self.area is not None:
      oprot.writeFieldBegin('area', TType.STRUCT, 2)
      self.area.write(oprot)
      oprot.writeFieldEnd()
    if self.seconds is not None:
      oprot.writeFieldBegin('seconds', TType.I64, 3)
      oprot.writeI64(self.seconds)
      oprot.writeFieldEnd()
    if self.search_filter is not None:
      oprot.writeFieldBegin('search_filter', TType.STRUCT, 4)
      self.search_filter.write(oprot)
      oprot.writeFieldEnd()
    oprot.writeFieldStop()
    oprot.writeStructEnd()

  def validate(self):
    return


  def __hash__(self):
    value = 17
    value = (value * 31) ^ hash(self.biz)
    value = (value * 31) ^ hash(self.area)
    value = (value * 31) ^ hash(self.seconds)
    value = (value * 31) ^ hash(self.search_filter)
    return value

  def __repr__(self):
    L = ['%s=%r' % (key, value)
      for key, value in self.__dict__.iteritems()]
    return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

  def __eq__(self, other):
    return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

  def __ne__(self, other):
    return not (self == other)