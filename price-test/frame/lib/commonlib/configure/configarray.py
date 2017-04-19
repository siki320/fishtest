#!/usr/bin/env python
# -*- coding: GB18030 -*-
'''
Created on 2012-3-10

@author: tongdangdang
'''

from types import *

import configunit
import configgroup 

class ConfigArray(object):
    '''
    @author: tongdangdang
    @summary: configure array
    '''
    def __init__(self, name, level, father, sep = ":"):
        self.name = name
        self.level = level
        self.father = father
        self.sep = sep
        self.note = ""
        self.data = []
        
    '''
    @summary: str()
    '''
    def __str__(self):
        ret_str = ""
        for obj in self.data:
            ret_str += obj.note
            if isinstance(obj,configunit.ConfigUnit):
                ret_str += "@" + obj.key + self.sep + str(obj) + '\n'
            else:
                ret_str += str(obj)
        return ret_str
    '''
    @summary: __getitem__
    '''
    def __getitem__(self,idx):
        if isinstance(idx,int):
            if idx+1 > len(self.data) or idx < -1:
                raise AssertionError,"idx:[%d] out of configure array range [0:%d]" % (idx,len(self.data)-1)
            else:
                return self.data[idx]
        else:
            raise AssertionError,"can only accept int as param for operator [],but input %s" % type(idx)
        
    '''
    @summary: __setitem__
    '''
    def __setitem__(self,idx,value):
        if isinstance(idx,int):
            if type(value) in [configunit.ConfigUnit,configgroup.ConfigGroup,ConfigArray]:
                self.level = value.level
            elif type(value) in [str]:
                self.level = -1
                value = configunit.ConfigUnit(self.name, value, self)
            else:
                raise AssertionError,"value must an instance ConfigUnit|ConfigGroup|ConfigArray|Str,but input [%s]" % type(value)
                
            if idx < -1 or idx > len(self.data):
                raise AssertionError,"idx:[%d] out of configure array range less than 0" % (idx)
            elif idx == len(self.data):
                self.data.append(value)
            else:
                self.data[idx] = value
        else:
            raise AssertionError,"can only accept int as param for operator [],but input %s" % type(idx)
        
    def __delitem__(self, idx):
        if isinstance(idx, int):
            if idx < -1 or idx > len(self.data) - 1:
                raise AssertionError,"idx:[%d] out of configure array range less than 0 or bigger than %d" % (idx,len(self.data))
            del self.data[idx]
        else:
            raise AssertionError, "can only accept int as param for operator [],but input %s" % type(idx)
    '''
    @summary: get add idx
    '''
    def _get_add_idx(self):
        return len(self.data)
    
    '''
    @summary: add
    '''
    def add(self,value):
        self.__setitem__(self._get_add_idx(), value)

    '''
    @author: zhaiyao
    @summary: return the first configunit(after startpos) in this array 
    '''
    def find(self, key, value, startpos = 0):
        if startpos < 0 or startpos > len(self.data) -1:
            raise AssertionError, "idx:[%d] out of configure array range less than 0 or bigger than %d" %(startpos,len(self.data))
        for index in range(startpos,len(self.data)):
            if str(self.data[index][key]) == str(value):
                return self.data[index]
        return None

    def findpos(self, key, value, startpos = 0):
        if startpos < 0 or startpos > len(self.data) -1:
            raise AssertionError, "idx:[%d] out of configure array range less than 0 or bigger than %d" %(startpos,len(self.data))
        for index in range(startpos,len(self.data)):
            if str(self.data[index][key]) == str(value):
                return index
        return None


    def __len__(self):
        return len(self.data)
    
    class Iterator():
        def __init__(self, array):
            self._position = 0
            self.data = array
        def next(self):
            if self._position  >= len(self.data.data):
                raise StopIteration
            obj = self.data.data[self._position]
            self._position = self._position + 1
            return obj
        
    def __iter__(self):
        return self.Iterator(self)
    
    '''
    @author: wangyue01
    @summary: configarray slice operation
    '''
    def __getslice__(self, i, j):
        return self.data[max(0, i):max(0, j):]
    
    def __setslice__(self, i, j, seq):
        self.data[max(0, i):max(0, j):]  = seq
        
    def __delslice__(self, i, j):
        del self.data[max(0, i):max(0, j):]
