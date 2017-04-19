#!/usr/bin/env python
#-*- encoding:utf-8 -*-
import os
import re

class ParseSvnDiff(object):
    desc = """ 解析svn_diff文件 """

    def __init__(self, svn_diff_file):
        """ 初始化 """
        self.svn_diff_file = svn_diff_file
        self.py_file_list = []
        self.cpp_file_list = []
        self.h_file_list = []
        self.block_dict = {}
        pass
        
    def parse_svn_diff(self):
        """ 获得svn_diff中的block，返回dict，key:file_name, value:list(start,end)"""

        if not os.path.exists(self.svn_diff_file):
            print "svn diff file :"+self.svn_diff_file+" is not exist"
            return -1
        
        svnfile_fp = open(self.svn_diff_file, 'r')
        lines=svnfile_fp.readlines()
        type_num = 0
        last_is_sub=False
        file_mod_start=0
        block_start=0
        block_end=0
        is_del_file=False
        file_name=""
        for line in lines:
            if re.search('^---', line) is not None or re.search('^\+\+\+', line) is not None:
                last_is_sub=False
                continue
            if re.search('^Index: ', line) is not None:
                """解决整个文件删除，添加所有新的内容，下一个文件开始先写一次"""
                if block_start != 0 and block_end != 0:
                    if self.block_dict.has_key(file_name)==True:
                        node_list=[block_start, block_end]
                        self.block_dict[file_name].append(node_list)
                    block_start=0
                    block_end=0
                    
                last_is_sub=False
                line_fields=line.split(' ')
                if len(line_fields)<2:
                    break
                file_name=line_fields[1][:-1]
                continue
            if re.search('^@@', line) is not None:
                last_is_sub=False
                is_del_file=False
                temp1=re.search("\+[0-9]+,[0-9]+", line)
                if temp1 is None:
                    block_start=0
                    block_end=0
                    continue
                temp=temp1.group()
                
                file_mod_start_str=temp.split(',')[0][1:]
                file_mod_start=int(file_mod_start_str)-1
                if file_mod_start != -1:
                    if self.block_dict.has_key(file_name)==False:
                        self.block_dict[file_name]=[]
                        if re.search('\.py', file_name) is not None:
                            self.py_file_list.append(file_name)
                        if re.search('\.cpp', file_name) is not None:
                            self.cpp_file_list.append(file_name)
                        if re.search('.\h', file_name) is not None:
                            self.h_file_list.append(file_name)
                block_start=0
                block_end=0
                continue

            if re.search('^\+', line) is not None:
                file_mod_start+=1
                if block_start == 0 or last_is_sub == True:
                    block_start=file_mod_start
                    block_end=file_mod_start
                else:
                    block_end=file_mod_start
                last_is_sub=False
                continue
                
            if re.search('^-', line) is not None and file_mod_start != -1:
                last_is_sub=True
                if block_start == 0:
                    block_start=file_mod_start
                    block_end=file_mod_start
                else:
                    block_end=file_mod_start
                continue

            """ last is not not modify code line"""
            if block_start != 0 and block_end != 0 or last_is_sub:
                if self.block_dict.has_key(file_name)==True:
                    node_list=[block_start, block_end]
                    self.block_dict[file_name].append(node_list)
                block_start=0
                block_end=0
            file_mod_start+=1
            last_is_sub=False
        #for key in self.block_dict.keys():
        #    print key
        #    print self.block_dict[key]
        return 0
    
    def get_diff_pyfile(self):
        """ diff py name"""
        return self.py_file_list

    def get_diff_cppfile(self):
        """ diff py name"""
        return self.cpp_file_list

    def get_diff_hfile(self):
        """ diff py name"""
        return self.h_file_list

    def get_svndiff_block(self):
        """ svn diff block """
        return self.block_dict
    
    def have_diff(self, file_name, start_line, end_line):
        """ have diff """
        start_line_int=int(start_line)
        end_line_int=int(end_line)
        if len(file_name) == 0:
            return False
        if self.block_dict.has_key(file_name)==False:
            return False
        else:
            for block in self.block_dict[file_name]:
                if start_line_int >= block[0] and start_line_int <= block[1] or \
                    start_line_int <= block[0] and end_line_int >= block[0] or \
                    start_line_int <= block[1] and end_line_int >= block[1]:
                    return True
        return False

