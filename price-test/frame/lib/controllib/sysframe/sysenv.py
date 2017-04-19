# -*- coding: GB18030 -*-
"""
@author: songyang
@date: Feb 24, 2014
@summary: ϵͳ����ģʽ�Ļ�����Զ�̵��ȿ��
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
	    ������̬���֣�ģ�������Լ�lib·��������, �Լ�bash_profile�ı���
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
            ������̬topo���֣�ģ��Ļ����Լ�·���������ӵ���Ϣ
        '''
        self.topo = EnvConfigHelper.get_conf(self.topology_file_dir,self.topology_file)
        if self.topo.type == 'mm' or self.topo.type == 'mmub':
            return self._parse_topo_mm()
        else:
            return XDFrameError,'topology file type error'
        
    def _parse_conf_mm(self):
        """
        @author: tianhu
        @param  topology_file:���˽ṹ�ļ�
        @note:  �������˽ṹ���������˽ṹ��������Ӧ�Ķ��󣬲�����������ϵ
        """
        #��ȡԶ�̴��Ҫ�Ļ���������Ϣ����conf_file�е�remote_bash_profile��Ϣ
        self._set_remote_bash_profile(self.conf)

        #��������������Ϣ����conf_file�е�module_class��Ϣ
        if self.conf.get_conf_version() == "3":
            module_name = self.conf.parse_module_name_dict()
            if module_name != None:
                self.module_name_dict = module_name

        return 0

    def _parse_topo_mm(self):
        """
        @author:tianhu
        @param  topology_file:���˽ṹ�ļ�
        @note:  �������˽ṹ���������˽ṹ��������Ӧ�Ķ��󣬲�����������ϵ
        """
        #����ģ����Ϣ
        host_info_list,module_info_list = self.topo.parse_host_module()
        if host_info_list == None:
            return 1
                
        for host_info in host_info_list:
            self.reg_host_info(host_info["host_name"].strip(),host_info["user"],host_info["password"])

        #����xstp���»����б�,��ģ����Ϣ
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

        #�Զ���������ģ��Ķ���
        for module_info in module_info_list:
            self.reg_module_info(module_info)
            self.reg_host_in_module(module_info)

        #��ʼ�����в��Ի�
        self.init_hosts()

        #ʵ����ģ�����
        self.instantiate_modules()

        #����������Ϣ
        topology_info_list = self.topo.parse_topology()       

        #�Զ�����������ϵ
        for topology_info in topology_info_list:
            self._relate_module(topology_info)

        return 0

    def instantiate_module(self,module_info):
        '''
        @author:    geshijing
        @note:      ʵ����ģ�����Զ�̵Ķ���ʹ��RPYCʵ����������ʵ����֮ǰ��Ҫ����reg_module_infoע��ģ����Ϣ
        @param module_info: ģ����Ϣ
        '''
        #��Ҫע���ģ��������bdbs1
        module_name  = module_info["module_name"]
        class_name = module_info["class_name"]

        #��Ҫ�����ģ��,����Novabsӳ�䵽nova_bs.Novabs����ô��Ҫfrom nova_bs import Novabs
        from_module = ".".join(self.module_name_dict[class_name].split(".")[0:-1])
        import_module = self.module_name_dict[class_name].split(".")[-1]
        #sys.path.append(os.path.expanduser("~/.XDS_CLIENT"))

        tmpmod = __import__(from_module,globals(),locals(),[import_module],-1)

        #��������,�����б������Ƕ�̬��
        setattr(self,module_name,getattr(tmpmod,import_module)(instance_name=module_name,local_path=module_info["remote_path"],
                host=module_info["host_name"],user=module_info["user"],passwd=module_info["password"]))
        #ע�����
        self._register_module(getattr(self,module_name))

    def _set_remote_bash_profile(self,conf_ins):
        """
        @note:����޸�ֻ����һ�ε�ִ�й�������Ч������Ӱ����������������������path�Ļ�
              ��Ҫ���⴦��
              ���û����topologicfile�����ø�ֵ�Ļ����Ͳ������û�������
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
