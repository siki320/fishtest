# -*- coding: GB18030 -*-
'''
Created on Sep 9, 2011

@author: caiyifeng<caiyifeng>

@summary: touch��ǿ�棬ǿ�Ƹ����ļ�ʱ���
'''

import os
import time

from frame.lib.commonlib.dtssystem import dtssystem


def touchex(filepath, *compare_files):
    '''
    @summary: ����Ӧtouch
    @note: 1. ��filepath��
     - 2. �����е�compare_files�£�������0��1Ŀ¼���µ������
     - 3. >= ��ǰʱ��
    '''
    if not os.path.exists(filepath):
        # �ļ������ڣ���Ҫ��touch����
        dtssystem("touch "+filepath)
        
    # ����ʱ���
    _updatetime(filepath, *compare_files)
        
def _updatetime(filepath, *compare_files):
    '''
    @summary: ����filepath��ʱ���
    @note: 1. ��filepath��
     - 2. �����е�compare_files��
     - 3. >= ��ǰʱ��
    '''
    # ��¼����ʱ���
    times = []
    
    # ��¼filepathʱ���
    st = os.stat(filepath)
    times.extend([st.st_atime, st.st_mtime, st.st_ctime])
    
    # ��¼����compare_files��ʱ���
    for f in compare_files:
        if os.path.exists(f):
            st = os.stat(f)
            times.extend([st.st_atime, st.st_mtime, st.st_ctime])
            
    # ����ʱ���
    max_time = max(times) + 1                   # ��filepath�����е�compare_files����
    max_time = max(max_time, time.time())       # >=��ǰʱ��
    os.utime(filepath, (max_time, max_time))


def _test():
    # touchһ�������ڵ��ļ�
    touchex("a.txt")
    print dtssystem("ls --full-time a.txt; date", output=True)[1]
    print
    
    # touchһ�ٴΣ�Ӧ�ø�һ��δ����ʱ��
    for i in range(100):
        touchex("a.txt")
    print dtssystem("ls --full-time a.txt; date", output=True)[1]
    print
    
    # b.txt��a.txt����
    touchex("b.txt", "a.txt")
    print dtssystem("ls --full-time b.txt; date", output=True)[1]

if __name__ == "__main__":
    _test()
