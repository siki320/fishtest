# -*- coding: GB18030 -*-
"""
@author: guoan & maqi
@copyright: Copyright (c) 2011 XX, Inc. All Rights Reserved
"""

import os
import re

from threading import Thread,Lock
from datetime import datetime, timedelta

from frame.lib.hbdblib.util import *
from frame.lib.hbdblib.error import HBDBError
from frame.lib.commonlib.dtssystem import dtssystem
from frame.lib.commonlib.dlog import dlog

class HBDBBase(object):
    def __init__(self, user, *args, **kwargs):
        self.user = user

    def install_client(self):
        pass

    def detect_client():
        pass

    def apply_space(self):
        pass

    def raw_rm(self,src):
        pass

    def raw_mkdir(self,src):
        pass

    def raw_ls(self,src):
        pass

    def raw_put(self,src,des):
        pass

    def raw_inc_put(self,src,des):
        pass

    def raw_get(self,src,des):
        pass

    def raw_inc_get(self,src,des):
        pass

    def raw_md5(self,dir):
        pass

    def md5(self,dir):
        cmd = self.raw_md5(src)
        dlog.info(cmd)
        return dtssystem(cmd)

    def mkdir(self,src):
        cmd = self.raw_mkdir(src)
        dlog.info(cmd)
        return dtssystem(cmd)

    def rm(self,src):
        cmd = self.raw_rm(src)
        dlog.info(cmd)
        return dtssystem(cmd)

    def ls(self,src):
        cmd = self.raw_ls(src)
        dlog.info(cmd)
        data = dtssystem(cmd,output=True)[1]
        dlog.info(data)
        return data

    def put(self,src,dest,thread_num=3):
        return self.multi_thread_upload(src,dest,thread_num)

    def get(self,src,dest,thread_num=3):
        return self.multi_thread_download(src,dest,thread_num)

    def sync_put(self, dir, module="test_module", label="test_label", is_multi=True, thread_num=3):
        """
        @notice: hbdb定位为data的管理者，对于conf、bin暂时不考虑
                 data的组织格式为/user/self.user/module/[date]/label
                 上传计算md5生成一个md5文件 @todo
        @param dir: local_path
        @param module: module name
        @param label: label name
        @param is_multi: TRUE or FALSE
        @param thread_num: thread nums (defalt 3)
        """
        des = self.cal_put_des(module,label)
        if is_multi == True:
            return self.multi_thread_upload(dir,des,thread_num)
        else:
            return self.single_upload(dir,des)

    def cal_put_des(self,module,label):
        std_day = datetime.now()
        return "/user/%s/%s/%s/%s" % (self.user,module,std_day.strftime("%Y%m%d"),label)

    def sync_get(self, dir, module="test_module", label="test_label", is_multi=True, thread_num=3, delta_day=-1):
        """
        @notice: hbdb定位为data的管理者，对于conf、bin暂时不考虑
                 data的组织格式为/user/self.user/module/[date]/label
                 下载对比md5，进行通用下载 @todo
        @param dir: local_path
        @param module: module name
        @param label: label name
        @param is_multi: TRUE or FALSE
        @param thread_num: thread nums (defalt 3)
        @param delta_day: now just used for mode (down)
        """
        src = self.cal_get_src(module,label,delta_day)
        if is_multi == True:
            return self.multi_thread_download(src,dir,thread_num)
        else:
            return self.single_download(src,dir)

    def cal_get_src(self,module,label,delta_day):
        std_day = datetime.now()
        appointed_day = (std_day + timedelta(days=delta_day)).strftime("%Y%m%d")
        return "/user/%s/%s/%s/%s" % (self.user,module,appointed_day,label)

    def single_upload(self,src,dest):
        cmd = self.raw_put(src,dest)
        dlog.info(cmd)
        return dtssystem(cmd)

    def inc_upload(self,src,dest):
        cmd = self.raw_inc_put(src,dest)
        dlog.info(cmd)
        return dtssystem(cmd)

    def single_thread_upload(self,src_path,upload_file_list,dest_path,rlock):
        while len(upload_file_list) <> 0:
            rlock.acquire()
            #获取下载的资源路径
            if len(upload_file_list) <> 0:
                one_file = upload_file_list.pop()
            rlock.release()
            postfix = re.sub(src_path,"",one_file)
            self.single_upload(one_file,dest_path+"/"+postfix.lstrip("/"))
        return 0

    def multi_thread_upload(self,src_path,dest_path,thread_num):
        """
        @notice: 针对目录，可以多起几个线程同时上传，限制为3个最大
                 超过三个也没有太大的意义
        """
        if src_path == "":
            return 1
        if not os.path.isabs(src_path):
            src_path = os.path.abspath(src_path)
        file_list = get_upload_file_list(src_path)
        threads=[]
        rlock=Lock()
        for i in range(thread_num):
            p=Thread(target=self.single_thread_upload, args=[src_path,file_list,dest_path,rlock])
            threads.append(p)

        for i in range(thread_num):
            threads[i].start()

        for i in range(thread_num):
            threads[i].join()

    def single_download(self,src,dest):
        cmd = self.raw_get(src,dest)
        dlog.info(cmd)
        return dtssystem(cmd)

    def inc_download(self,src,dest):
        cmd = self.raw_inc_get(src,dest)
        dlog.info(cmd)
        return dtssystem(cmd)

    def single_thread_download(self,src_path,download_file_list,dest_path,rlock):
        while len(download_file_list) <> 0:
            rlock.acquire()
            #获取下载的资源路径
            if len(download_file_list) <> 0:
                one_file = download_file_list.pop()
            rlock.release()
            postfix = re.sub(src_path,"",one_file)
            self.single_download(one_file,dest_path+"/"+postfix.lstrip("/"))
        return 0

    def multi_thread_download(self,src_path,dest_path,thread_num):
        if src_path == "":
            return 1
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)
        file_list = get_download_file_list(self,src_path)
        threads=[]
        rlock=Lock()
        for i in range(thread_num):
            p=Thread(target=self.single_thread_download, args=[src_path,file_list,dest_path,rlock])
            threads.append(p)

        for i in range(thread_num):
            threads[i].start()

        for i in range(thread_num):
            threads[i].join()
