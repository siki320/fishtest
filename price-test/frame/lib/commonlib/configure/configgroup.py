#!/usr/bin/env python
# -*- coding: GB18030 -*-
'''
Created on 2012-3-10

@author: tongdangdang
'''

from types import *
from collections import OrderedDict


import configunit 
import configarray 


class ConfigGroup(object):
    '''
    @author: tongdangdang
    @summary: configure group
    '''
    def __init__(self, name, level, father, note="", sep = ":"):
        self.name = name
        self.level = level
        self.father = father
        self.note = note
        self.sep = sep
        self.data = OrderedDict()
        
    def __str__(self):
        if isinstance(self.father,configarray.ConfigArray):
            name = "@"+self.name
        else:
            name = self.name
        ret_str ='['+'.'*(self.level-1)+name+']\n'
     #   self.data = OrderedDict(sorted(self.data.items(), key=lambda t: t[0]))
        for key in self.data:
            if self.data[key].level == -1:
                ret_str += self.data[key].note
                if isinstance(self.data[key],configunit.ConfigUnit):
                    if isinstance(self.data[key].father,configarray.ConfigArray) and (self.data[key].father.name == key):
                        ret_str += "@"+key+ self.sep + str(self.data[key]) +"\n"
                    else:
                        ret_str += key + self.sep + str(self.data[key]) +"\n"
                        
                else:
                    ret_str += str(self.data[key])
        for key in self.data:           
            if self.data[key].level != -1:
                ret_str += self.data[key].note
                ret_str += str(self.data[key])
        return ret_str
        
    '''
    @summary: __getitem__
    '''
    def __getitem__(self,key):
        if isinstance(key,str): 
            if key not in self.data:
                #raise AssertionError,"key:[%s] is not in confiure group:[%s]" % (key,self.name)
                return None
            return self.data[key]
        else:
            raise AssertionError,"can only support str as a key for configure group"
        
    '''
    @summary: __setitem__
    '''
    def __setitem__(self,key,value):
        if isinstance(key,str):
            if type(value) in [configunit.ConfigUnit,configarray.ConfigArray, ConfigGroup]:
                self.data[key] = value
            elif isinstance(value,str):
                if key in self.data:
                    self.data[key].value = value
                else:
                    self.data[key] = configunit.ConfigUnit(key,value,"")
            else:
                raise AssertionError,"value can only type in [ConfigUnit,ConfigArray,ConfigGroup],but %s" % (type(value),)
        else:
            raise AssertionError,"key expect str type not [%s]" % (type(key),)
    
    def __delitem__(self, key):
        if self.data.has_key(key):
            del self.data[key]

    '''
    @summary: get all key and value of a section, store to dict
    @need by quanxi
    '''
    def get_key_dict(self):
        key_value_dict = {}
        for key in self.data.keys():
            if type(self.data[key]) in [configunit.ConfigUnit]:
                key_value_dict[key] = str(self.data[key].value)

            elif type(self.data[key]) in [ configarray.ConfigArray ]:
                key_value_dict[key] = []
                for group in self.data[key]:
                    if type( group ) in [configunit.ConfigUnit]:
                        key_value_dict[key].append( str( group.value ) )
                    else: 
                        key_value_dict[key].append( group.get_key_dict() )

            elif type(self.data[key]) in [ type(self) ]:
                key_value_dict[key] = self.data[key].get_key_dict()

        return key_value_dict

    '''
    @summary: get all key and value of a section
    @need by Li Peilong
    '''
    def get_key_value(self):
        key_value_list = []
        for key in self.data.keys():
            if type(self.data[key]) in [configunit.ConfigUnit]:
                key_value_list.append([key, self.data[key].value])
        return key_value_list
    
    def has_key(self, key):
        if isinstance(key,str): 
            if key not in self.data:
                #raise AssertionError,"key:[%s] is not in confiure group:[%s]" % (key,self.name)
                return False
            return True
        else:
            raise AssertionError,"can only support str as a key for configure group"
               
