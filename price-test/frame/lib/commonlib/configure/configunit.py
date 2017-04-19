#!/usr/bin/env python
# -*- coding: GB18030 -*-
'''
Created on 2012-3-10

@author: tongdangdang
'''

class ConfigUnit(object):
    '''
    @author: tongdangdang
    @summary: ub conf configure unit
    '''
    def __init__(self,key,value,father,note = ""):
        self.key = key
        self.value = value
        self.level = -1
        self.father = father
        self.note = note
        
    '''
    @summary: user defined str
    '''
    def __str__(self):
        return self.value

    def __getitem__(self, key):
        return self.value

    #def __delitem__(self, key):
    #    if isinstance(self.father, configarray.ConfigArray):
    #        pass
    #    elif isinstance(self.father, configarray.ConfigArray):
    #        pass
