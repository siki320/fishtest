# -*- coding: GB18030 -*-
'''
Created on May 25, 2011

@author: caiyifeng

@summary: ��־��ȡģ��
'''

import os
from frame.lib.commonlib.dlog import dlog


class LogReader(object):
    def __init__(self, logpath):
        self.logpath = logpath
        self.pos = 0
        
        self.begin()        # ��ʼ��ʱ����λ��־��ʼλ��
        
    def begin(self):
        '''
        @note: ��λ��־��ʼλ��
        '''
        if not os.path.isfile(self.logpath):
            # ��־�ļ�������
            dlog.debug("Log file not exists. Set pos to 0: %s", self.logpath)
            self.pos = 0
            return
        
        f = open(self.logpath)
        f.seek(0, os.SEEK_END)  # �ƶ����ļ�ĩβ
        self.pos = f.tell()
        f.close()
        
    def read(self):
        '''
        @note: ��ȡbegin��ʼ����־
        @return: ������־�ַ���
        '''
        if not os.path.isfile(self.logpath):
            # ��־�ļ���������
            dlog.debug("Log file not exists yet. Return empty string: %s", self.logpath)
            return ""
        
        f = open(self.logpath)
        
        f.seek(0, os.SEEK_END)  # �ƶ����ļ�ĩβ
        size = f.tell()
        
        if size >= self.pos:
            f.seek(self.pos, os.SEEK_SET)   # �ƶ���beginλ��
            ret = f.read(size - self.pos)
        else:
            # size < self.pos
            # ��־��������ͷ��ʼ
            f.seek(0, os.SEEK_SET)      # �ƶ����ļ�ͷ
            ret = f.read(size)
        
        f.close()
        
        return ret
    
    def read_last_lines(self, linenum):
        '''
        @note: ��ȡ���linenum��
        '''
        string = self.read()
        lines = string.splitlines(True)[-linenum:]   # ȡ���linenum��
        
        return "".join(lines)
    
    def read_fatal_and_last_lines(self, linenum):
        '''
        @note: ��ȡFATAL��־ & ���linenum��
        '''
        string = self.read()
        lines = string.splitlines(True)
        
        if len(lines) <= linenum:
            # ��־����linenum�У���ȡ����
            f_lines = lines
        else:
            lines1 = lines[:-linenum]
            lines2 = lines[-linenum:]
            
            f_lines = []
            
            # lines1�ҳ����е�FATAL��
            for l in lines1:
                if l.startswith("FATAL:"):
                    f_lines.append(l)
                    
            # lines2ȫ������
            f_lines.extend(lines2)
            
        return "".join(f_lines)
    
    
def _test_log_reader():
    fn = raw_input("Input log file: ")
    
    # �����޹�����
    f = open(fn, "a")
    f.write("FATAL:aaa\n")
    f.flush()
    
    # ������־��ȡ
    lr = LogReader(fn)
    
    # ����һ��fatal�к�һ����ͨ��
    f.write("FATAL: bbbb\n")
    f.flush()
    f.write("bbbb\n")
    f.flush()
    print lr.read()
    
    # ��������
    f.write("ccc\nFATAL:dddd\n")
    f.flush()
    print lr.read()
    
    print lr.read_last_lines(2)
    print lr.read_fatal_and_last_lines(2)
    
    f.close()

if __name__ == "__main__":
    _test_log_reader()

