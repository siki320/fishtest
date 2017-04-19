# -*- coding: GB18030 -*-
"""
@author: maqi
"""

import os
from frame.lib.hbdblib.base import HBDBBase
from frame.lib.commonlib.dtssystem import dtssystem

class TDW(HBDBBase):
    def __init__(self, user, *args, **kwargs):
        #每一个产品线需要一个用户名
        super(TDW, self).__init__(user, *args, **kwargs)

        #这个路径分配的是一个产品线的主入口路径
        self.tdw_path = "/test/%s" % (self.user)
        #client 放置路径
        self.client_path = os.path.expanduser("~/.TDW_CLIENT")
        #可执行文件路径
        self.tdw_bin_path = self.client_path + "/tdw/client/bin/tdw"
        self.hadoop_bin_path = self.client_path + "/tdw/client/bin/hadoop"
        #init os env
        if os.environ.has_key("JAVA_HOME") == False:
            os.environ["JAVA_HOME"] = "%s/tdw/java6/"%(self.client_path)

    def apply_space(self,user,disk_space = "10T"):
        pass

    def install_client(self):
        wget_str = "wget --limit-rate=40m ftp://"
        tar_str = "tar -xzf tdw.tar.gz"
        dtssystem(wget_str)
        dtssystem("mkdir -p %s;mv tdw.tar.gz %s"%(self.client_path,self.client_path))
        dtssystem("cd %s;%s"%(self.client_path,tar_str))

    def detect_client(self):
        if os.path.isdir(self.client_path):
            output = dtssystem("%s fs -ls" % (self.hadoop_bin_path))
        return output

    #hadoop 基本命令封装
    def raw_put(self,src,des):
        return "%s -put %s %s" % (self.tdw_bin_path,src,des)

    def raw_get(self,src,des):
        return "%s -get %s %s" % (self.tdw_bin_path,src,des)

    def raw_mkdir(self,src):
        return "%s fs -mkdir -p %s" % (self.hadoop_bin_path,src)

    def raw_ls(self,src):
        return "%s fs -ls %s" % (self.hadoop_bin_path,src)

    def raw_rm(self,src):
        return "%s fs -rmr %s" % (self.hadoop_bin_path,src)
