# -*- coding: GB18030 -*-
"""
@author: youguiyan01
@date: Mar 5, 2012
@summary: md5计算
@version: 1.0.0.0
@copyright: Copyright (c) 2012 XX, Inc. All Rights Reserved
"""
import os
import hashlib
import sys
import re
class MD5:
    """
    @note: md5计算类,支持计算文件和目录的md5值，同时运行添加 ignore列表
    """

    def __init__(self):
        self._ignore_list = []
        self.result = []

    def __str__(self):
        """
        @note: 输出到string中，每行一个文件，第一个值是MD5，第二个是地址
        """

        result_list = []
        for result in self.result:
            if len(result) ==2:
                result_list.append(result["md5"]+"  "+ result["path"])
        return "\n".join(result_list)
    
    def add_ignore(self,file_name):
        """
        @note: 添加过滤列表，支持正则表达式，不区分文件还是文件夹，只要路径中含有该词，都会被过滤
        @param file_name:需要过滤的名字
        """
        self._ignore_list.append(file_name)
        
    def _md5_file(self,file_path,seg_num=128,read_power=0):
        """
        @note: 计算文件的md5值,对文件分段，从每一段中读取一定长度的值进行md5计算
        @param file_path:文件路径
               seg_num: 文件分段的个数 
               read_power:每次读取长度的指数
        @return result字典，key有md5和path两个 
        """
        result = {}
        result["path"] = file_path
        #read_size最小是2*13
        read_size = 2**(13+read_power)
        fp = open(file_path,"rb")
        #文件大小，在分段中加入文件大小的因素
        file_size = os.path.getsize(file_path)
        md5_value = hashlib.md5()
        #分段的个数，如果读的长度太大，可能导致没有办法分这么多段，
        #因此在这里去两个的最小值
        seg_num = file_size/read_size > seg_num and seg_num or file_size/read_size+1
        for i in range(seg_num):
            #定位到该段的初始位置
            skig_size = (i*file_size)/seg_num
            fp.seek(skig_size,0)
            #读read_size长度的内容
            tmp = fp.read(read_size)
            if not tmp:
                break
            #更新md5值
            md5_value.update(tmp)

        result["md5"]=md5_value.hexdigest()
        fp.close()
        return result

    def _is_ignore(self,path):
        """
        @note:  判断是否在过滤列表中，需要被过滤
        @return True:需要被过滤
                False:不需要被过滤
        @param  path:需要判断的路径
        """
        for pattern in self._ignore_list:
            if re.search(pattern,path):
                return True
        return False
    def _md5_dir(self,file_path,seg_num=8096,read_power=0):
        """
        @note: 计算目录的md5，进行递归调用 
        @param file_path:文件路径
               seg_num: 文件分段的个数 
               read_power:每次读取长度的指数
        @return 返回值是一个列表，列表中每一个元素都是字典
                key有md5和path两个 
        """
        result = []
        dirs = os.listdir(file_path)
        for one_dir in dirs:
            path = file_path + os.sep + one_dir
            #判断是否在过滤列表中
            if self._is_ignore(path):
                continue
            if os.path.isdir(path):
                result += self._md5_dir(path,seg_num,read_power)
            else:
                result += [self._md5_file(path,seg_num,read_power)]
        return result

    def md5sum(self,file_path,seg_num=8096,read_power=0):
        """
        @note: 计算md5 
        @param file_path:文件路径
               seg_num: 文件分段的个数 
               read_power:每次读取长度的指数
        @return 返回值是一个列表，列表中每一个元素都是字典
                key有md5和path两个 
        """
        self.result = []
        #文件
        if os.path.isfile(file_path):
            #单个文件需要单独判断是否需要过滤
            if self._is_ignore(file_path):
                self.result =[]
            else:
                self.result = [self._md5_file(file_path,seg_num,read_power)]
        #目录
        elif os.path.isdir(file_path):
            self.result = self._md5_dir(file_path,seg_num,read_power)
        else: 
            self.result = []
        return self.result

if __name__== "__main__":
    import sys
    a=MD5()
    a.add_ignore("svn")
    a.add_ignore("test")
    a.md5sum(sys.argv[1],128,10)
    print str(a)
