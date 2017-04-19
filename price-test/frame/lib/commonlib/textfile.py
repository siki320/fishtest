# -*- coding: GB18030 -*-
'''
Created on Apr 8, 2011

@author: caiyifeng
'''

class TextFile(object):
    '''
    @note: �ı��ļ��Ļ���
    '''
    def __init__(self, filepath):
        self.filepath = filepath
        self.lines = []     # ÿ��Ԫ�����ı��У����������з���
        
    def add_line(self, line):
        self.lines.append(line)
        
    def __str__(self):
        return "".join(line + "\n" for line in self.lines)
        
    def dump(self):
        fout = open(self.filepath, "w")
        fout.write(str(self))
        fout.close()
        
