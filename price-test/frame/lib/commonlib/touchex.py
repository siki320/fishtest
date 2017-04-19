# -*- coding: GB18030 -*-
'''
Created on Sep 9, 2011

@author: caiyifeng<caiyifeng>

@summary: touch增强版，强制更新文件时间戳
'''

import os
import time

from frame.lib.commonlib.dtssystem import dtssystem


def touchex(filepath, *compare_files):
    '''
    @summary: 自适应touch
    @note: 1. 比filepath新
     - 2. 比所有的compare_files新（适用于0，1目录更新等情况）
     - 3. >= 当前时间
    '''
    if not os.path.exists(filepath):
        # 文件不存在，需要先touch生成
        dtssystem("touch "+filepath)
        
    # 更新时间戳
    _updatetime(filepath, *compare_files)
        
def _updatetime(filepath, *compare_files):
    '''
    @summary: 更新filepath的时间戳
    @note: 1. 比filepath新
     - 2. 比所有的compare_files新
     - 3. >= 当前时间
    '''
    # 记录所有时间戳
    times = []
    
    # 记录filepath时间戳
    st = os.stat(filepath)
    times.extend([st.st_atime, st.st_mtime, st.st_ctime])
    
    # 记录所有compare_files的时间戳
    for f in compare_files:
        if os.path.exists(f):
            st = os.stat(f)
            times.extend([st.st_atime, st.st_mtime, st.st_ctime])
            
    # 更新时间戳
    max_time = max(times) + 1                   # 比filepath和所有的compare_files都新
    max_time = max(max_time, time.time())       # >=当前时间
    os.utime(filepath, (max_time, max_time))


def _test():
    # touch一个不存在的文件
    touchex("a.txt")
    print dtssystem("ls --full-time a.txt; date", output=True)[1]
    print
    
    # touch一百次，应该赋一个未来的时间
    for i in range(100):
        touchex("a.txt")
    print dtssystem("ls --full-time a.txt; date", output=True)[1]
    print
    
    # b.txt比a.txt更新
    touchex("b.txt", "a.txt")
    print dtssystem("ls --full-time b.txt; date", output=True)[1]

if __name__ == "__main__":
    _test()
