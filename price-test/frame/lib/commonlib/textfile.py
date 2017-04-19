# -*- coding: GB18030 -*-
'''
Created on Apr 8, 2011

@author: caiyifeng
'''

class TextFile(object):
    '''
    @note: 文本文件的基类
    '''
    def __init__(self, filepath):
        self.filepath = filepath
        self.lines = []     # 每个元素是文本行（不包括换行符）
        
    def add_line(self, line):
        self.lines.append(line)
        
    def __str__(self):
        return "".join(line + "\n" for line in self.lines)
        
    def dump(self):
        fout = open(self.filepath, "w")
        fout.write(str(self))
        fout.close()
        
