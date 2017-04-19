# -*- coding: GB18030 -*-
'''
'''
import traceback
from frame.lib.controllib.normal.normal_case import NormalCase, NormalPlugin
from frame.lib.commonlib.dlog import dlog
from frame.lib.commonlib import asserts
from frame.lib.commonlib.utils import rename_cores, log_cores
from frame.lib.commonlib.logreader import LogReader
from frame.lib.commonlib.asserts import assert_equal

class MyCase(NormalCase):
    def __new__(cls):
        obj = NormalCase.__new__(cls)
        obj.mp = MyCase_Plugin()
        return obj
        
        
    def _decode_list(self, data, charset="utf-8"):
        rv = []
        for item in data:
            if isinstance(item, unicode):
                item = item.encode(charset)
            elif isinstance(item, list):
                item = _decode_list(item)
            elif isinstance(item, dict):
                item = _decode_dict(item)
            rv.append(item)
        return rv
        
    def _decode_dict(self, data,charset="utf-8"):
        rv = {}
        for key, value in data.iteritems():
            if isinstance(key, unicode):
                key = key.encode(charset)
            if isinstance(value, unicode):
                value = value.encode(charset)
            elif isinstance(value, list):
                value = _decode_list(value,charset)
            elif isinstance(value, dict):
                value = _decode_dict(value)
            rv[key] = value
        return rv
        
class MyCase_Plugin(NormalPlugin):
    # def benchmark_env(self):
    #     dlog.info("[Plugin] Benchmark env ...")
    #     ############### init && prepare depend
    #     self.query = Re_Query()
    #     self.query.clean_env()
    #     self.query.prepare_env()

    def startup_env(self):
        dlog.info("[Plugin] startup env ...")


    def stop_env(self):
        dlog.info("[Plugin] stop_env ...")

    def clean_error(self):
        pass

    def common_check(self, acase):
        dlog.info("[Plugin] Common check ...")
        #if os.path.isdir(EnvGlobal.QUERY_PATH):
        #    log_cores(EnvGlobal.QUERY_PATH)
        #if os.path.isdir(EnvGlobal.ROUTER_PATH):
        #    log_cores(EnvGlobal.ROUTER_PATH)

    def diagnose_error(self):
        dlog.diagnose("[Plugin] Diagnose errors Module")

    def bak_failed_env(self, relpath):
        dlog.info("[Plugin] Bak failed  env ")
