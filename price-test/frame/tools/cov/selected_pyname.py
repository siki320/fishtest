#!/usr/bin/env python
#-*- encoding:utf-8 -*-
import string
import os

class Selected_Pyname(object):
    def __init__(self):
        """  ��ʼ������ """
        pass
        
    def get_selected_pyname(self):
        """ ��ȡ��ѡ���py��������list"""
        selected_pylist = []
        if os.path.exists(".select_pyname.txt"):
            select_py_fp=open(".select_pyname.txt","r")
            lines = select_py_fp.readlines()
            selected_pylist = lines[0].split(" ")
            selected_pylist.sort()
            select_py_fp.close()
        
        return selected_pylist

    def write_selected_pyname(self, pyname_list=[]):
        """ ��ѡ�����py��д���ļ� """
        py_str=string.join(pyname_list," ")
        select_py_fp=open(".select_pyname.txt","w")
        select_py_fp.write(py_str)
        select_py_fp.close()
     
