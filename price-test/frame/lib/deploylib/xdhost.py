# -*- coding: GB18030 -*-
"""
@author: geshijing
@date: Nov 1, 2012
@summary: 测试机管理类
@version: 0.0.0.1
@copyright: Copyright (c) 2012 XX, Inc. All Rights Reserved
"""
import os
from frame.lib.deploylib.basemodule import RpycTypeMixIn
from frame.lib.deploylib.xdsystem import XDSystem
from frame.lib.commonlib.dlog import dlog


class XDHost(object):
    """docstring for XDHost"""
    def __init__(self,host_name,usr,passwd,home_path='.XDS_CLIENT'):
        self.host_name = host_name
        self.usr = usr
        self.passwd = passwd
        self.home_path = home_path

    def get_sign(self):
        return self.host_name +self.usr

    def set_log_sys(self,log,system):
        self.log = log
        self.sys = system

    def __getstate__(self):
        odict = self.__dict__.copy()
        del odict["log"]
        del odict["sys"]
        return odict

    def __setstate__(self,state):
        self.__dict__.update(state)
        self.log = dlog
        self.sys = XDSystem(self.log)

    def build_xds_client(self):
        """
        @note:必须先调用_set_remote_bash_profile,然后才能调用本函数
              具体原因是shell会使用一些环境变量
        """
        python_path = self.home_path
        deploylib_path = os.environ["xds_framelib_path"]+"/lib/deploylib"

        is_force_dispatch = ''
        if os.environ.has_key("xds_force_dispatch"):
            is_force_dispatch = os.environ["xds_force_dispatch"]
        dispatch_switch = '1'
        if is_force_dispatch == '0' or is_force_dispatch == 'false' or is_force_dispatch == 'False':
            dispatch_switch = '0'

        is_force_rpyc_start = ''
        if os.environ.has_key("xds_force_rpyc_start"):
            is_force_rpyc_start = os.environ["xds_force_rpyc_start"]
        rpyc_start_switch = '1'
        if is_force_rpyc_start == '0' or is_force_rpyc_start == 'false' or is_force_rpyc_start == 'False' \
                and ping(socket.gethostbyname(host), int(RpycTypeMixIn.DEFAULT_RPC_PORT)) == 0:
            rpyc_start_switch = '0'

        cmd = 'cd  %s;sh build_xds_client.sh %s %s %s %s %s %s' % (deploylib_path,self.host_name,
                self.usr,self.passwd,dispatch_switch,rpyc_start_switch,python_path)
        self.log.info(cmd)
        self.sys.xd_system(cmd,output=True,pflag=True)
        return 0
