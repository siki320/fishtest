# -*- coding: GBK -*-
"""
    @author     : yuanyi03
    @date       : Tue 19 Mar 2013 11:09:59 AM CST
    @last update: Tue 19 Mar 2013 11:09:59 AM CST
    @summary    : system case. 
                  Has no bussiness with how to run test
    @version    : 1.0.0.0
"""

import sys
from frame.lib.commonlib.safe_encode import safegb
from frame.lib.commonlib.relpath import get_relpath

def enum(*seq, **kv):
    enum = dict(zip(seq, range(len(seq))),**kv)
    return type("Enum",(),enum)

class Sys_Case(object):
    
    STATS = enum("LOAD_FAILED",
            "INSTANCE_FAILED",
            "ENVCONF_MISS",
            "READY")

    def __init__(self):
        self.status=Sys_Case.STATS.READY
        self.filepath = "" #case 路径
        self.confpath= None # deploy的配置文件路径
        self.modules={}
        pass

    def load_modules(self, modules):
        ''' load libs what you want from deploy's modules '''
        for m in modules:
            self.modules[m['instance_name']] = m['module']
        return 0

    def get_module(self, mod_name):
        if m not in self.modules.keys():
            return None
        return self.modules[mod_name]

    def set_status(self,status):
        self.status = status
        
    def set_envconf(self,confpath):
        self.confpath = confpath

    def get_envconf(self):
        return self.confpath

    def set_filepath(self, filepath):
        self.filepath = filepath
    
    def get_filepath(self):
        return self.filepath

    def get_relpath(self):
        return get_relpath(self.filepath)

    def set_desc(self, desc):
        if desc:
            self.desc = safegb(desc).strip()

    def setup_testcase(self):
        pass

    def setup(self):
        pass

    def teardown(self):
        pass

    def teardown_testcase(self):
        pass

    def bak_failed_env(self,case_name):
        pass
