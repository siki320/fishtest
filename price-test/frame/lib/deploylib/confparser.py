# -*- coding: GB18030 -*-
"""
@author: lipeilong
@date: Mar 28, 2012
@summary: �������������ļ��Ľ���
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
    @note:Env��������Helper��
    """
    @staticmethod
    def get_conf(file_dir,file):
        """
        @note:����Env��������
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
    @note:������������Env�����˽ṹ
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
                #ֻ�з�ע����
                #if False == self._check_line_is_comments(line):
                continue

            up_module, down_module = self._parse_module_name(line)
            return_topology_list.append([up_module,down_module])
        return return_topology_list

    def _check_line_is_empty(self, line):
        '''
        @note: ����Ƿ�Ϊ����
        '''
        if "\n" != line[-1]:
            return False

        for c in line[:-1]:
            if " " != c:
                return False

        return True

    def _check_line_is_comments(self, line):
        '''
        @note: ���line�ǲ���һ��ע���У�����
        '''
        if True == self._check_line_is_empty(line):
            return True

        #��������#�����϶�����ע����
        pos = string.find(line, "#")

        if -1 == pos:
            return False

        #ע��ֻ�жϵ�һ����#��, line�ĵ�һ���ǿո��ַ��ǡ�#��,��ʾ��ע����
        #���￼������Ч��β��ע��
        ret = True
        for c in line[:pos]:
            if " " != c:
                ret = False
                break

        return ret

    def _check_line_validity(self, line):
        '''
        @note:���line�ĺϷ���
        '''
        ret = True
        #line�м� ��������->�����ֲ�������<-��
        if -1 == string.find(line, "->") and -1 == string.find(line, "<-"):
            ret = False
        #line�м� ������->�����ְ�����<-��
        if -1 != string.find(line, "->") and -1 != string.find(line, "<-"):
            ret = False

        #����ǲ���ע����
        if True == self._check_line_is_comments(line):
            ret = False

        return ret

    def _parse_module_name(self, line):
        '''
        @note: �ӺϷ���line��parse��������ģ����
        '''
        sep_list = ["->", "<-"]

        for s in sep_list:
            if -1 != string.find(line, s):
                sep = s
                break

        module_name_list = line.split(sep)

        # �Ϸ�line���к���˵����ע�ͣ����˵�ע��
        if -1 != module_name_list[1].find("#"):
            module_name_list[1] = module_name_list[1][0:module_name_list[1].index("#")]

        #�� "->", "<-"�ж�������ģ��
        up_module_name = module_name_list[sep_list.index(sep)].strip()
        down_module_name = module_name_list[1 - sep_list.index(sep)].strip()
        return up_module_name, down_module_name


class EnvMMConfigParser(object):
    """
    @author:youguiyan01
    @note:����Env�����˽ṹ
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
        @note: ��ȡhost�е�����host����Ϣ��Ȼ�����ÿһ��host��
                Ѱ�Ҹ�host�����ģ����Ϣ��Ȼ�����ƴ��
        @return return_module_list��ģ����Ϣ�б���list��ÿһ��Ԫ�ض�һ��ģ����Ϣ���������
                ģ�������������������ļ������ַ���������û���������
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
        @note:��������
        @return return_topology_list:�����б�ÿ��Ԫ����һ��������ϵ
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
    @note:�����°汾��Env���˽ṹ�����ļ���֧�ֶ༶section���ã�conf.version=3
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
        @note: ��ȡlib class��Ӧ��lib·����Ϣ
        """
        return_module_name_dict={}

        if self.conf["module_class"] == None:
            return None

        for module_name in self.conf["module_class"].get_key_value():
            return_module_name_dict[module_name[0]] = module_name[1]
        return return_module_name_dict

    def parse_host_module(self):
        """
        @note: ��ȡhost�е�����host����Ϣ��Ȼ�����ÿһ��host��
                Ѱ�Ҹ�host�����ģ����Ϣ��Ȼ�����ƴ��
        @return return_module_list��ģ����Ϣ�б���list��ÿһ��Ԫ�ض�һ��ģ����Ϣ���������
                ģ�������������������ļ������ַ���������û���������
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
            #����module��Ϣ
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
        @note:��������
        @return return_topology_list:�����б�ÿ��Ԫ����һ��������ϵ
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

