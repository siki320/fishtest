# -*- coding: GB18030 -*-
"""
@author: lipeilong
@date: Mar 28, 2012
@summary: 负责拓扑配置文件的解析
@version: 1.0.0.0
@copyright: Copyright (c) 2012 XX, Inc. All Rights Reserved
"""

import os
import string
import ConfigParser
from frame.lib.commonlib.configure.configure import Configure


class EnvConfigHelper(object):
    """
    @author:maqi
    @note:Env拓扑配置Helper类
    """
    @staticmethod
    def get_conf(file_dir,file):
        """
        @note:生成Env拓扑配置
        """
        if file is None:
            return None
        try:
            conf = EnvMMConfigParser(file_dir, file)
            if conf.get_conf_version() == "3":
                conf = EnvMMUbConfigParser(file_dir, file)
        except ConfigParser.MissingSectionHeaderError:
            conf = EnvSMConfigParser(file_dir,file)

        return conf


class EnvSMConfigParser(object):
    """
    @author:maqi
    @note:解析单机部署Env的拓扑结构
    """
    def __init__(self,file_dir,file):
        self.type = 'sm'
        if file == None:
            self.lines = None
        else:
            f = open(file_dir+file, 'r')
            self.lines = f.readlines()
            f.close()
    def get_conf_version(self):
        return "1"

    def parse_topology(self):
        return_topology_list = []
        line_count = 0
        for line in self.lines:
            line_count += 1
            if False == self._check_line_validity(line):
                #只有非注释行
                #if False == self._check_line_is_comments(line):
                continue

            up_module, down_module = self._parse_module_name(line)
            return_topology_list.append([up_module,down_module])
        return return_topology_list

    def _check_line_is_empty(self, line):
        '''
        @note: 检查是否为空行
        '''
        if "\n" != line[-1]:
            return False

        for c in line[:-1]:
            if " " != c:
                return False

        return True

    def _check_line_is_comments(self, line):
        '''
        @note: 检查line是不是一个注释行，空行
        '''
        if True == self._check_line_is_empty(line):
            return True

        #不包含“#”，肯定不是注释行
        pos = string.find(line, "#")

        if -1 == pos:
            return False

        #注意只判断第一个“#”, line的第一个非空格字符是“#”,表示被注释了
        #这里考虑了有效行尾的注释
        ret = True
        for c in line[:pos]:
            if " " != c:
                ret = False
                break

        return ret

    def _check_line_validity(self, line):
        '''
        @note:检查line的合法性
        '''
        ret = True
        #line中既 不包含“->”，又不包含“<-”
        if -1 == string.find(line, "->") and -1 == string.find(line, "<-"):
            ret = False
        #line中既 包含“->”，又包含“<-”
        if -1 != string.find(line, "->") and -1 != string.find(line, "<-"):
            ret = False

        #检查是不是注释行
        if True == self._check_line_is_comments(line):
            ret = False

        return ret

    def _parse_module_name(self, line):
        '''
        @note: 从合法的line中parse出上下游模块名
        '''
        sep_list = ["->", "<-"]

        for s in sep_list:
            if -1 != string.find(line, s):
                sep = s
                break

        module_name_list = line.split(sep)

        # 合法line的中含有说明类注释，过滤掉注释
        if -1 != module_name_list[1].find("#"):
            module_name_list[1] = module_name_list[1][0:module_name_list[1].index("#")]

        #由 "->", "<-"判断上下游模块
        up_module_name = module_name_list[sep_list.index(sep)].strip()
        down_module_name = module_name_list[1 - sep_list.index(sep)].strip()
        return up_module_name, down_module_name


class EnvMMConfigParser(object):
    """
    @author:youguiyan01
    @note:解析Env的拓扑结构
    """
    def __init__(self,file_dir,file):
        self.type = 'mm'
        self.conf = ConfigParser.SafeConfigParser()
        self.conf.read(file_dir+file)

    def get_conf_version(self):
        return str(self._get_info("conf","version"))

    def _get_section(self,section):
        if not self.conf.has_section(section):
            return None
        return self.conf.items(section)

    def _get_info(self,section_name, key_name):
        if self.conf.has_option(section_name, key_name) == False:
            return None
        info = self.conf.get(section_name, key_name)
        return info

    def parse_host_module(self):
        """
        @note: 读取host中的所有host的信息，然后对于每一个host，
                寻找该host下面的模块信息，然后进行拼接
        @return return_module_list：模块信息列表，该list中每一个元素都一个模块信息，具体包含
                模块名，类名，类描述文件，搭建地址，主机，用户名，密码
        """
        return_host_list = []
        return_module_list = []
        host_list = self._get_section("host")
        if host_list == None:
            return None
        for host in host_list:
            host_name = host[0]
            temp_info = host[1].split("\t")
            host_info={}
            host_info["host_name"] = temp_info[0]
            host_info["user"] = temp_info[1]
            host_info["password"] = temp_info[2]
            return_host_list.append(host_info)
            module_info_list = self._get_section(host_name)
            if module_info_list == None:
                #return None
                continue
            for one_module_info in module_info_list:
                module_name = one_module_info[0]
                temp_info = one_module_info[1].split("\t")
                module_info = {}
                module_info["module_name"] = module_name
                module_info["class_name"] = temp_info[0]
                module_info["conf_file"] = temp_info[1]
                module_info["remote_path"] = temp_info[2]
                module_info.update(host_info)
                return_module_list.append(module_info)
        return return_host_list,return_module_list

    def parse_topology(self):
        """
        @note:解析拓扑
        @return return_topology_list:拓扑列表，每个元素是一个关联关系
                (up_module,down_module)
        """
        return_topology_list = []
        topology_list = self._get_section("topology")
        if topology_list == None:
            return return_topology_list
        for topology in topology_list:
            topology_info = topology[1].split("->")
            if len(topology_info) <= 1:
                continue
            up_module = topology_info[0].strip(" ")
            down_module = topology_info[1].strip(" ")
            return_topology_list.append([up_module,down_module])
        return return_topology_list


class EnvMMUbConfigParser(object):
    """
    @author:lipeilong
    @note:解析新版本的Env拓扑结构配置文件，支持多级section配置，conf.version=3
    """
    def __init__(self, conf_dir, conf_file):
        self.type = 'mmub'
        self.conf=Configure()
        self.conf.load(conf_dir, conf_file)
        self.dir = conf_dir
        self.file = conf_file

    def get_conf_version(self):
        return str(self._get_info("conf","version"))
    
    def _get_section(self,section):
        key_value_list = self.conf[section].get_key_value()
        return key_value_list

    def _get_info(self,section_name, key_name):
        info = self.conf[section_name][key_name]
        if info == None:
            return None
        value = str(info)
        return value

    def parse_module_name_dict(self):
        """
        @note: 读取lib class对应的lib路径信息
        """
        return_module_name_dict={}

        if self.conf["module_class"] == None:
            return None

        for module_name in self.conf["module_class"].get_key_value():
            return_module_name_dict[module_name[0]] = module_name[1]
        return return_module_name_dict

    def parse_host_module(self):
        """
        @note: 读取host中的所有host的信息，然后对于每一个host，
                寻找该host下面的模块信息，然后进行拼接
        @return return_module_list：模块信息列表，该list中每一个元素都一个模块信息，具体包含
                模块名，类名，类描述文件，搭建地址，主机，用户名，密码
        """
        return_host_list = []
        return_module_list = []

        index = 0
        host_num = len(self.conf["deploy"]["host"])
        while index < host_num:
            host_info={}
            host_info["host_name"] = str(self.conf["deploy"]["host"][index]["name"])
            if self.conf["deploy"]["host"][index].has_key('user'):
                host_info["user"] = str(self.conf["deploy"]["host"][index]["user"])
            if self.conf["deploy"]["host"][index].has_key('password'):
                host_info["password"] = str(self.conf["deploy"]["host"][index]["password"])
            return_host_list.append(host_info)
            #解析module信息
            index_module = 0
            module_num = len(self.conf["deploy"]["host"][index]["module"])
            while index_module < module_num:
                module_info = {}
                module_info["module_name"] = str(self.conf["deploy"]["host"][index]["module"][index_module]["name"])
                module_info["class_name"] = str(self.conf["deploy"]["host"][index]["module"][index_module]["class"])
                module_info["conf_file"] = str(self.conf["deploy"]["host"][index]["module"][index_module]["conf"])
                if self.conf["deploy"]["host"][index]["module"][index_module].has_key("remote_path"):
                    module_info["remote_path"] = str(self.conf["deploy"]["host"][index]["module"][index_module]["remote_path"])
                else:
                    module_info["remote_path"] = module_info["module_name"]
                if self.conf["deploy"]["host"][index]["module"][index_module].has_key("cpuCoreNum"):
                    module_info["cpuCoreNum"] = str(self.conf["deploy"]["host"][index]["module"][index_module]['cpuCoreNum'])
                if self.conf["deploy"]["host"][index]["module"][index_module].has_key("mem"):
                    module_info["mem"] = str(self.conf["deploy"]["host"][index]["module"][index_module]['mem'])
                if self.conf["deploy"]["host"][index]["module"][index_module].has_key("disk"):
                    module_info["disk"] = str(self.conf["deploy"]["host"][index]["module"][index_module]['disk'])
                if self.conf["deploy"]["host"][index]["module"][index_module].has_key("exclusive"):
                    module_info["exclusive"] = str(self.conf["deploy"]["host"][index]["module"][index_module]['exclusive'])
                module_info.update(host_info)
                return_module_list.append(module_info)
                index_module = index_module + 1
            index = index + 1

        return return_host_list, return_module_list

    def parse_topology(self):
        """
        @note:解析拓扑
        @return return_topology_list:拓扑列表，每个元素是一个关联关系
                (up_module,down_module)
        """
        return_topology_list = []
        index = 0
        topo_list = self.conf["deploy"]["topology"].get_key_value()
        for relation in topo_list:
            topology_info = relation[1].split("->")
            if len(topology_info) <= 1:
                continue
            up_module = topology_info[0].strip(" ")
            down_module = topology_info[1].strip(" ")
            return_topology_list.append([up_module,down_module])
            index = index + 1

        return return_topology_list

