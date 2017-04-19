#!/usr/bin/env python
# -*- coding: GB18030 -*-

"""
@author:xuwei03
2012.9.14

"""

import os
import sys
import re
import string
from frame.tools.cov.ParseSvnDiff import *


class GetDiffCasePlus(object):
    case_list = {}
    py_files = []
    parse_svndiff = None
    svn_diff_file = ''
    def __init__(self,svn_diff,svn_type,svn_path="./"):
        self.case_lis = []
        self.py_files = []
        self.svn_diff_file = svn_diff
        self.svn_type = svn_type
        self.svn_path = svn_path
        self.parse_svndiff = ParseSvnDiff(self.svn_diff_file)
        self.parse_svndiff.parse_svn_diff()
        pass


    def getPyFileCaseline(self,file):
        """
        得到case文件中每个test的行号
        """
        if file == '':
            print 'the file is NULL'
            return {}
        try:
            if self.svn_type == "rb":
                f = open("../"+file,'r')
            if self.svn_type == "trunk":
                f = open(file,'r')
            if self.svn_type == "imas_trunk":
                f = open("../"+file,'r')
            if self.svn_type == "ctr":
                f = open(self.svn_path+"/"+file,'r')
        except IOError,e:
            print 'could not open the file'
            return {}
        res_tests = {}
        index = 0
        test_lines = []
        test_names = []
        i = 0
        s = 0
        e = 0
        for line in f:
            index += 1
            test_tag = re.search('^ +def test[^\(]*',line)
            tear_tag = re.search('^ +def tearDown[^\(]*',line)
            setup_tag = re.search('^ +def setUp[^\(]*',line)
            if test_tag is not None:
                test = re.search('test[^\(]*',test_tag.group())
                test_names.append(test.group())
                test_lines.append(index)
            elif tear_tag is not None:
                teardown = "tearDown"
                test_names.append(teardown)
                test_lines.append(index)
            elif setup_tag is not None:
                setup = "setUp"
                test_names.append(setup)
                test_lines.append(index)
        max = len(test_lines)
        for name in test_names:
            s = test_lines[i]
            if i != max-1:
                e = test_lines[i+1]-1
            else:
                e = index-1
            res_tests[name]=[s,e]
            i += 1
        return res_tests
        pass
        

    def getDiffCase(self):
        """
        得到py文件中变化的case
        """
        tests = []
        self.py_files = self.parse_svndiff.get_diff_pyfile()
        #print self.py_files
        for i in self.py_files:
            if re.search('case\/',i) is None:
                continue
            res_tests = self.getPyFileCaseline(i)
            test_list = []
            is_get_all_case = False
            for key in res_tests:
                is_diff = self.parse_svndiff.have_diff(i,int(res_tests[key][0]),int(res_tests[key][1]))
                if key == "setUp" or key == "tearDown":
                    if is_diff:
                        is_get_all_case = True
                        break
                else:
                    if is_diff:
                        test_list.append(key)
                    else:
                        continue
            if is_get_all_case == True:
                for key in res_tests:
                    if key != "setUp" and key != "tearDown":
                        test_list.append(key)
            self.case_list[i] = test_list
        for key in self.case_list.keys():
            for case_name in self.case_list[key]:
                if self.svn_type == "rb":
                    tests.append(string.replace(key, "cts/", "")+":"+case_name)
                if self.svn_type == "trunk":
                    tests.append(string.replace(key, "../cts/", "")+":"+case_name)
                if self.svn_type == "imas_trunk":
                    tests.append(string.replace(key, "cts/", "")+":"+case_name)
                if self.svn_type == "ctr":
                    tests.append(key+":"+case_name)
        return tests
        pass
                   
    def printCases(self):
        """
        打印选出的test
        """
        for key in self.case_list:
            for case in self.case_list[key]:
                print "%s:" % key,case
        pass

    def getAddCase(self):
        """
        获得增加的case
        """
        pass

    def getDelCase(self):
        """
        获得删除的case
        """
        pass

    def getModCase(self):
        """
        获得变化的case
        """
        pass
