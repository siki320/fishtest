# -*- coding: GB18030 -*-
"""
@author: songyang
@date: Feb 24, 2014
@summary: 系统集成模式的环境和远程调度框架
@version: 1.1.0.0
@copyright: Copyright (c) 2014 XX, Inc. All Rights Reserved
"""

import inspect
import string
import os
import sys
import ConfigParser
import pickle
import socket
import traceback
from copy import deepcopy
from frame.lib.commonlib.dlog import dlog
from frame.lib.commonlib.utils import get_abs_dir,get_current_path
from frame.lib.commonlib.timer import Timer2

from frame.lib.deploylib.basemodule import BaseModule,RpycTypeMixIn
from frame.lib.deploylib.xdhost import XDHost
from frame.lib.deploylib.utils import ping
from frame.lib.deploylib.xderror import XDFrameError
from frame.lib.deploylib.confparser import EnvConfigHelper
from frame.lib.deploylib.result import Env_result
from frame.lib.commonlib.portalloc import PortAlloc
from frame.lib.deploylib.framework import Env

class SysEnv(Env):
    def __init__(self,log=dlog,auto_dispatch=False,auto_module_path=False):
        super(SysEnv,self).__init__(log,auto_dispatch,auto_module_path)
        self.topology_file=''
        self.topology_file_dir=''
        self.conf_file=''
        self.conf_file_dir=''

    def deploy(self,is_download=True,is_xstp=False):
        self._parse_conf(self.conf_file, self.conf_file_dir)
        self._parse_topology(self.topology_file, self.topology_file_dir) 
        self.single_thread_run("download_env")
        #self.single_thread_run("start_env")
        self.single_thread_run("set_relations")

    def set_conf_file(self, conf_file=''):
        self.conf_file = os.path.basename(conf_file)
        self.conf_file_dir = os.path.dirname(conf_file) + '/'

    def set_topology_file(self, topology_file=''):
        self.topology_file = os.path.basename(topology_file)
        self.topology_file_dir = os.path.dirname(topology_file) + '/'

    def _parse_conf(self, config_file, config_file_dir):
        '''
        @author: tianhu
        @note:
	    解析静态部分，模块设置以及lib路径等配置, 以及bash_profile的变量
        '''
        self.conf = EnvConfigHelper.get_conf(self.conf_file_dir,self.conf_file)
        if self.conf.type == 'mm' or self.conf.type == 'mmub':
            return self._parse_conf_mm()
        elif self.conf is None or self.conf.type == 'sm':
            return
        else:
            return XDFrameError,'config file type error'

    def _parse_topology(self, topology_file, topology_file_dir):
        '''
        @author: tianhu
        @note:
            解析动态topo部分，模块的机器以及路叮拓扑连接等信息
        '''
        self.topo = EnvConfigHelper.get_conf(self.topology_file_dir,self.topology_file)
        if self.topo.type == 'mm' or self.topo.type == 'mmub':
            return self._parse_topo_mm()
        else:
            return XDFrameError,'topology file type error'
        
    def _parse_conf_mm(self):
        """
        @author: tianhu
        @param  topology_file:拓扑结构文件
        @note:  解析拓扑结构，根据拓扑结构，创建相应的对象，并建立关联关系
        """
        #获取远程搭建需要的环境变量信息，即conf_file中的remote_bash_profile信息
        self._set_remote_bash_profile(self.conf)

        #解析部署配置信息，即conf_file中的module_class信息
        if self.conf.get_conf_version() == "3":
            module_name = self.conf.parse_module_name_dict()
            if module_name != None:
                self.module_name_dict = module_name

        return 0

    def _parse_topo_mm(self):
        """
        @author:tianhu
        @param  topology_file:拓扑结构文件
        @note:  解析拓扑结构，根据拓扑结构，创建相应的对象，并建立关联关系
        """
        #解析模块信息
        host_info_list,module_info_list = self.topo.parse_host_module()
        if host_info_list == None:
            return 1
                
        for host_info in host_info_list:
            self.reg_host_info(host_info["host_name"].strip(),host_info["user"],host_info["password"])

        #根据xstp更新机器列表,和模块信息
        if self.is_xstp:
            for host_info in self.xstp_host_info_list:
                self.reg_host_info(host_info["host"].strip(),host_info["applyUser"],host_info["applyPassword"])
                for  module_info in module_info_list:
                    if module_info["module_name"]==host_info["moduleName"]:
                        module_info["host_name"] = host_info["host"].strip()
                        module_info["user"] = host_info["applyUser"]
                        module_info["password"] = host_info["applyPassword"]
                        module_info["remote_path"] = host_info["workPath"]
        if module_info_list == None:
            return 1

        #自动创建各个模块的对象
        for module_info in module_info_list:
            self.reg_module_info(module_info)
            self.reg_host_in_module(module_info)

        #初始化所有测试机
        self.init_hosts()

        #实例化模块对象
        self.instantiate_modules()

        #解析拓扑信息
        topology_info_list = self.topo.parse_topology()       

        #自动创建关联关系
        for topology_info in topology_info_list:
            self._relate_module(topology_info)

        return 0

    def instantiate_module(self,module_info):
        '''
        @author:    geshijing
        @note:      实例化模块对象（远程的对象使用RPYC实例化），在实例化之前需要调用reg_module_info注册模块信息
        @param module_info: 模块信息
        '''
        #需要注册的模块名，如bdbs1
        module_name  = module_info["module_name"]
        class_name = module_info["class_name"]

        #需要导入的模块,比如Novabs映射到nova_bs.Novabs，那么需要from nova_bs import Novabs
        from_module = ".".join(self.module_name_dict[class_name].split(".")[0:-1])
        import_module = self.module_name_dict[class_name].split(".")[-1]
        #sys.path.append(os.path.expanduser("~/.XDS_CLIENT"))

        tmpmod = __import__(from_module,globals(),locals(),[import_module],-1)

        #创建对象,这里有变量名是动态的
        setattr(self,module_name,getattr(tmpmod,import_module)(instance_name=module_name,local_path=module_info["remote_path"],
                host=module_info["host_name"],user=module_info["user"],passwd=module_info["password"]))
        #注册对象
        self._register_module(getattr(self,module_name))

    def _set_remote_bash_profile(self,conf_ins):
        """
        @note:这个修改只在这一次的执行过程中有效，不会影响其他，但是如果想用这个path的话
              需要额外处理
              如果没有在topologicfile中设置该值的话，就不会设置环境变量
        @return:1 or 0
        """
        global_dict ={}
        for one_list in conf_ins._get_section("remote_bash_profile"):
            if one_list[0].endswith("_path"):
                apath = one_list[1]
                if not os.path.isabs(apath):
                    apath = os.path.join(self.conf_file_dir, apath)
                global_dict.update({one_list[0]:apath})
            else:
                global_dict.update({one_list[0]:one_list[1]})
        self.init_global(global_dict)
        return 0
