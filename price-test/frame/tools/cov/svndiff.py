#!/usr/bin/env python
# encoding: GB18030 
"""
incstatmentcov.py

Created by ypp on 2012-02-29.
"""
import commands
import os
import sys
import re
from datetime import datetime
from os.path import isfile, dirname, isdir

class CodeBlock:
    def __init__(self):
        self.startline = 0
        self.endline = 0
    def set_start_end(self,startline,endline):
        self.startline = startline
        self.endline = endline
    def get_start_end(self):
        return self.startline,self.endline

class SvnDiff:        
    def __init__(self,svn_file,result={},path=""):
        self.svn_diff = svn_file 
        self.result = result 
        if ""==path:
            self.path="./"
        else:
            self.path=path

    def index_of(self,str_,ch,idx):
        idx_found = 0
        len_ = len(str_)
        for i in range(0,len_,1):
            if  str_[i] == ch:
                idx_found += 1
                if idx_found == idx:
                    return i
        return -1
    def is_legal_file(self,path):
        ext_list = [".cc",".c",".cpp",".h",".hpp"]
        file_name = os.path.basename(path)
        name,ext = os.path.splitext(file_name)
        pattern = re.compile('unittest')
        ret = 0
        if (not pattern.search(path)) and ext in ext_list:
            ret = 1
        return ret

    def code_diff(self):
        flag = "Index"
        flag_len = len(flag)
        file_name = ""
        changed_indeed = 0
        line_no1 = 0
        line_no2 = 0
        skip_the_file = 0
        startline = 0
        prelabel = " "
        line_nu = 0
        fileIN = open(self.svn_diff, "r")
        for line in fileIN:
            line = line.strip('\n')
            if line[0:flag_len] == flag:
                file_name = line[flag_len+2:]
                if self.is_legal_file(self.path+"/"+file_name) == 1:
                    skip_the_file=0
                    self.result[file_name]=[]
                else:
                    skip_the_file=1
                changed_indeed=0
                continue
            if line[0:3] == "---" or line[0:3] == "+++" :
                continue
           # if line.strip() and 0x4e00<ord(line.strip()[0])<0x9fa6:
           #     continue
            if skip_the_file == 1:
                continue
            if line[0:2] == "@@":
                line_nu = 0
                prelabel = " "
                pattern = re.compile("^@@ \-[0-9]+,[0-9]+ \+0,0 @@$")
                if not pattern.match(line):
                    changed_indeed=1
                comma_idx = self.index_of(line, ",", 1)
                table_idx = self.index_of(line, " ", 2)
                line_no1 = int(line[4:comma_idx])
                ori_line = int(line[comma_idx+1:table_idx])
                plus_idx = self.index_of(line, "+", 1)
                comma_idx = self.index_of(line, ",", 2)
                table_idx = self.index_of(line, " ", 3)
                line_no2 = int(line[plus_idx+1:comma_idx])
                now_line = int(line[comma_idx+1:table_idx])
                max_line = int(max(ori_line,now_line))
            elif changed_indeed == 1:
                if line[0:1] == "-":
                    if prelabel == "+":
                        a = CodeBlock()
                        a.set_start_end(startline,line_no2-1)
                        self.result[file_name].append(a)
                    prelabel = "-"
                    line_no1 += 1
                elif line[0:1] == "+":
                    line_nu += 1
                    if prelabel != "+":
                        startline = line_no2
                    prelabel = "+"
                    line_no2 += 1
                    if line_nu == max_line :
                        a = CodeBlock()
                        a.set_start_end(startline,line_no2-1)
                        self.result[file_name].append(a)
                        
                else:
                    line_nu += 1
                    if prelabel == "+":
                        a = CodeBlock()
                        a.set_start_end(startline,line_no2-1)
                        self.result[file_name].append(a)
                    prelabel = " "
                    line_no1 += 1
                    line_no2 += 1
        fileIN.close()
        #return self.reslut
    #    for key in self.result:
    #        print "=====",key,"====",len(self.result[key])
    #        for block in self.result[key]:
    #            a,b = block.get_start_end()
    #            print a,b

                        
if __name__ == "__main__":
    sys.exit(main()) 
