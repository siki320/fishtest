# -*- coding: GB18030 -*-
'''
Created on Nov 9, 2011

@author: caiyifeng<caiyifeng>

@summary: DtestCase基类
'''

import logging
from StringIO import StringIO
from types import UnicodeType
from frame.lib.commonlib.safe_encode import safegb
from frame.lib.commonlib.utils import get_py_owner
from frame.lib.commonlib.relpath import get_relpath
from frame.lib.commonlib.dlog import dlog

class DTSStringIO(StringIO):
    """
    Rough handle the mixing of Unicode and 8-bit strings：
    just try gbk codec.
    """
    def getvalue(self):
        try:
            return StringIO.getvalue(self)
        except UnicodeError:
            ul = []
            for s in self.buflist:
                if isinstance(s, UnicodeType):
                    ul.append(s)
                else:
                    try:
                        ul.append(unicode(s,'gbk'))
                    except UnicodeError:
                        ul.append(unicode(s,'ascii',errors='replace'))

            self.buf += ''.join(ul)
            self.buflist = []
            return self.buf

class CasePriority(object):
    """@summary: case优先级，BVT, HIGH, LOW """
    BVT  = 1
    HIGH = 2
    LOW  = 4
    DEFAULT = 0xFFFFFFFF

    @staticmethod
    def str2value(str_prior):
        value = 0
        if str_prior.find("BVT")>=0: value |= CasePriority.BVT
        if str_prior.find("HIGH")>=0: value |= CasePriority.HIGH
        if str_prior.find("LOW")>=0: value |= CasePriority.LOW
        if value == 0:
            raise Exception, "%s format error"%str_prior
        return value

    @staticmethod
    def value2str(value):
        ret_str = ""
        if value&CasePriority.BVT: ret_str += "BVT"
        if value&CasePriority.HIGH: ret_str += "HIGH"
        if value&CasePriority.LOW: ret_str += "LOW"
        if ret_str == "":
            raise Exception, "%d value error"%value
        return ret_str


class DtestCase(object):
    priority = CasePriority.DEFAULT
    tests_bvt = []
    tests_high = []
    tests_low = []
    def __new__(cls):
        '''@summary: 先于__init__被调用, 生成所有属性'''
        obj = object.__new__(cls)

        # --- 具体case可读/写的成员 ---
        obj.enable = True   # 是否启用
        obj.tags = []       # tag列表

        # --- 子类只读的成员 ---
        obj.filepath = ""   # case绝对路径
        obj.desc = ""       # case所在模块的docstring, GB18030_SAFE
        obj.log_sh = None
        obj.log_stream = DTSStringIO()       # case 运行log
        obj.log_record_level = logging.DEBUG  # 默认记录DEBUG以上的日志

        return obj

    def start_log_record(self):
        self.log_sh = logging.StreamHandler(self.log_stream)
        self.log_sh.setLevel(self.log_record_level)
        self.log_sh.setFormatter(dlog.fmt_sh)
        dlog.logger.addHandler(self.log_sh)

    def stop_log_record(self):
        dlog.logger.removeHandler(self.log_sh)
        self.log_sh.close()

    # ----- mutator -----
    def set_filepath(self, filepath):
        self.filepath = filepath

    def set_desc(self, desc):
        if desc:
            self.desc = safegb(desc).strip()
    # ----- (end)mutator -----

    # ----- accessor -----
    def get_relpath(self):
        return get_relpath(self.filepath)

    def get_owner(self):
        return get_py_owner(self.filepath)

    def get_priority(self):
        return self.priority
    # ----- (end)accessor -----

