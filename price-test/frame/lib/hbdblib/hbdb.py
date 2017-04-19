# -*- coding: GB18030 -*-
"""
@author: guoan & maqi
@date: Sep 17, 2012
@summary: hbdb的基类
@version: 1.0.0.0
"""
import os
import shutil
from frame.lib.hbdblib.tdw import TDW
from frame.lib.hbdblib.hdfs import HDFS
from frame.lib.hbdblib.mfs import MFS
from frame.lib.hbdblib.hdc import HDC

from frame.lib.hbdblib.error import HBDBError

class HBDB(object):
    def __init__(self, mode=None, user=None, *args, **kwargs):
        self.set_user(user)
        self.set_mode(mode, args, kwargs)

    def set_user(self, user):
        self.user = user

    def set_mode(self, mode, *args, **kwargs):
        self.mode = mode
        if not mode:
            self._ins = None
        elif mode == "tdw":
            self._ins = TDW(self.user, *args, **kwargs)
        elif mode == "hdfs":
            self._ins = HDFS(self.user, *args, **kwargs)
        elif mode == "mfs":
            self._ins = MFS(self.user, *args, **kwargs)
        elif mode == "hdc":
            self._ins = HDC(self.user, *args, **kwargs)
        else:
            raise HBDBError("unknown mode")

    def __getattr__(self,name):
        assert self._ins
        return getattr(self._ins, name)

    def __setattr__(self,name,value):
        if name in ('mode','user','_ins'):
            object.__setattr__(self, name, value)
        else:
            assert self._ins
            setattr(self._ins,name,value)

    def __str__(self):
        return "hbdb in %s mode" % self.mode

    def __repr(self):
        return "hbdb in %s mode" % self.mode

def test():
    pass

if __name__ == '__main__':
    test()
