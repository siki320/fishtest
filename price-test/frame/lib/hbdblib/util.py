# -*- coding: GB18030 -*-
from itertools import izip
from frame.lib.commonlib.dtssystem import dtssystem
import os

def split_file_list(tmp_iter,num):
    split_list = list()
    for i in range(num):
        split_list.append(list())

    for i in range(len(tmp_iter)):
        split_list[i%num].append(tmp_iter[i])

    return split_list

def get_upload_file_list(src_path):
    file_list = []
    for root,dirs,files in os.walk(src_path,True):
        #for dir in dirs:
        #        print os.path.join(root, dir)
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list

def get_download_file_list(hbdb,src_path):
    file_list = []
    raw_data = hbdb.ls(src_path)
    raw_list = raw_data.splitlines()[1:]
    for one_element in raw_list:
        tmp_list = one_element.split(" ")
        #if tmp_list[-1].startswith(src_path):
        file_list.append(tmp_list[-1])
    return file_list

