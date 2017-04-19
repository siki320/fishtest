# -*- coding: GB18030 -*-
'''
Created on May 25, 2011

@author: caiyifeng

@summary: 日志读取模块
'''

import os
from frame.lib.commonlib.dlog import dlog


class LogReader(object):
    def __init__(self, logpath):
        self.logpath = logpath
        self.pos = 0
        
        self.begin()        # 初始化时，定位日志开始位置
        
    def begin(self):
        '''
        @note: 定位日志开始位置
        '''
        if not os.path.isfile(self.logpath):
            # 日志文件不存在
            dlog.debug("Log file not exists. Set pos to 0: %s", self.logpath)
            self.pos = 0
            return
        
        f = open(self.logpath)
        f.seek(0, os.SEEK_END)  # 移动到文件末尾
        self.pos = f.tell()
        f.close()
        
    def read(self):
        '''
        @note: 读取begin开始的日志
        @return: 返回日志字符串
        '''
        if not os.path.isfile(self.logpath):
            # 日志文件还不存在
            dlog.debug("Log file not exists yet. Return empty string: %s", self.logpath)
            return ""
        
        f = open(self.logpath)
        
        f.seek(0, os.SEEK_END)  # 移动到文件末尾
        size = f.tell()
        
        if size >= self.pos:
            f.seek(self.pos, os.SEEK_SET)   # 移动到begin位置
            ret = f.read(size - self.pos)
        else:
            # size < self.pos
            # 日志已满，从头开始
            f.seek(0, os.SEEK_SET)      # 移动到文件头
            ret = f.read(size)
        
        f.close()
        
        return ret
    
    def read_last_lines(self, linenum):
        '''
        @note: 读取最后linenum行
        '''
        string = self.read()
        lines = string.splitlines(True)[-linenum:]   # 取最后linenum行
        
        return "".join(lines)
    
    def read_fatal_and_last_lines(self, linenum):
        '''
        @note: 读取FATAL日志 & 最后linenum行
        '''
        string = self.read()
        lines = string.splitlines(True)
        
        if len(lines) <= linenum:
            # 日志不足linenum行，读取所有
            f_lines = lines
        else:
            lines1 = lines[:-linenum]
            lines2 = lines[-linenum:]
            
            f_lines = []
            
            # lines1找出所有的FATAL行
            for l in lines1:
                if l.startswith("FATAL:"):
                    f_lines.append(l)
                    
            # lines2全部加入
            f_lines.extend(lines2)
            
        return "".join(f_lines)
    
    
def _test_log_reader():
    fn = raw_input("Input log file: ")
    
    # 增加无关数据
    f = open(fn, "a")
    f.write("FATAL:aaa\n")
    f.flush()
    
    # 启动日志读取
    lr = LogReader(fn)
    
    # 增加一个fatal行和一个普通行
    f.write("FATAL: bbbb\n")
    f.flush()
    f.write("bbbb\n")
    f.flush()
    print lr.read()
    
    # 增加两行
    f.write("ccc\nFATAL:dddd\n")
    f.flush()
    print lr.read()
    
    print lr.read_last_lines(2)
    print lr.read_fatal_and_last_lines(2)
    
    f.close()

if __name__ == "__main__":
    _test_log_reader()

