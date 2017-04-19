# -*- coding: GB18030 -*-
"""
@author: guoan
@date: Nov 25, 2011
@summary: 记录各个模块下载源的路径
@version: 1.0.0.0
@copyright: Copyright (c) 2011 XX, Inc. All Rights Reserved
@modify: 目前这个模块的用途已经废弃，仅仅rpyc_port还在被使用
"""

rpyc_port="60777"

class Base_global_info(object):
    """
    @note:基本的global_info文件，我们都以一个dict表示，如果各个模块有特殊的需求的话，继承此类，重载下
          这个类和safedownload.py是强相关的，请注意修改
    """
    def __init__(self):
        #目前初始化的这几个值是为了测试需要，每次这个地方的字典需要初始化覆盖
        self.global_dict = {}

    def get_global_dict(self):
        """
        @note:获得global_dict
        """
        return self.global_dict

    def set_global_dict(self,path_dict):
        """
        @note:设置产品线私有的备份字典信息
        @param path_dict:私有的备份字典信息
        """
        self.global_dict = path_dict
        return 0

    def has_key(self,key):
        """
        @note:实现字典的has_key功能
        @param key:传入key
        @return :1 or 0
        """
        return self.global_dict.has_key(key)

    def get_global_dict_by_type(self, key):
        """
        @note:获取一个模块对应的dict
        @param key:传入模块的type值
        @return :该模块对应的dict词典,如果不包含该模块信息返回None
        """
        if self.has_key(key):
            return self.global_dict[key]
        else:
            return None

class Hadoop_global_info(Base_global_info):
    """
    @note:记录hadoop平台相关的信息
          如果使用的备份集群是noah的那个hadoop，请在此填写模块信息
    """
    def __init__(self):
        Base_global_info.__init__(self)
        self.hadoop_host=""

    def get_hadoop_host(self):
        """
        @note:获得hadoop_host
        """
        return self.hadoop_host

    def set_hadoop_host(self,host):
        """
        @note:设置hadoop的主机名
        @param host:hadoop入口主机域名
        """
        self.hadoop_host = host
        return 0

    def get_hadoop_dict_by_type(self, key):
        """
        @note:获取一个模块对应的dict
        @param key:传入模块的type值
        @return :该模块对应的dict词典,如果不包含该模块信息返回None
        """
        if self.has_key(key):
            return self.global_dict[key]
        else:
            return None

class Std_global_info(Base_global_info):
    """
    @note:记录标准的ftp下载地址信息，如果你的模块备份在某些机器上面，那么这个模块的信息将被用到
    """
    def __init__(self):
        Base_global_info.__init__(self)

class Scmpf_global_info(Base_global_info):
    """
    @note:记录scmpf  类型的源信息
    """
    def __init__(self):
        Base_global_info.__init__(self)
        self.scmpf_host=""
        self.scmpf_user=""
        self.scmpf_passwd=""
        
    def set_scmpf_host_info(self,host,user,passwd):
        """
        @note:设置scmpf的host信息
        @param host:host
        @param user:user
        @param passwd:passwd
        """
        self.scmpf_host=host
        self.scmpf_user=user
        self.scmpf_passwd=passwd
        return 0

    def get_scmpf_host_info(self):
        """
        @note:返回scmpf各个模块的信息
        """
        return self.scmpf_host,self.scmpf_user,self.scmpf_passwd


#这些全局变量是各个模块最重要的信息，在每个app运行的时候需要将各自模块的备份字典信息，传入此处
#请勿随意修改此处
hadoop_info = Hadoop_global_info()
std_info = Std_global_info()
scmpf_info = Scmpf_global_info()
