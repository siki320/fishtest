# -*- coding: GB18030 -*-
# '''
# Created on Dec 11, 2011
# @author: maqi<maqi>
# @summary: some utils
# '''

import cPickle as pickle
import json

class InterfaceMetaData(dict):
    def __init__(self):
        super(InterfaceMetaData,self).__setitem__('head',{})
        super(InterfaceMetaData,self).__setitem__('body',{})
        self.head_set_flag = False
        self.body_set_flag = False
    
    def __setitem__(self,key,value):
        if key == 'head':
            if isinstance(value,dict):
                super(InterfaceMetaData,self).__setitem__(key,value)
                self.head_set_flag = True
            else:
                raise TypeError,'only dict type is allowed'
        elif key == 'body':
            if isinstance(value,dict):
                super(InterfaceMetaData,self).__setitem__(key,value)
                self.body_set_flag = True
            else:
                raise TypeError,'only dict type is allowed'   
        else:
            raise AttributeError,'only head or body is allowed'
    
    def __str__(self):
        tmp_str =""
        #edited  by geshijing
        #fix eception when there's raw item in body
        try:
            tmp_str ="\n" + "\033[4;32m[HEAD]:\033[0m " + json.dumps(self.get("head"), ensure_ascii=False) + "\n" + "\033[4;34m[BODY]:\033[0m " + json.dumps(self.get("body"), ensure_ascii=False)
            # encode to gbk when result is unicode
            if type(tmp_str) == unicode:
                tmp_str = tmp_str.encode('utf-8')
        except:
            tmp_str ="\n" + "\033[4;32m[HEAD]:\033[0m " + str(self.get("head")) + "\n" + "\033[4;34m[BODY]:\033[0m " + str(self.get("body"))
        return tmp_str
    
    def clear(self):
        super(InterfaceMetaData,self).__setitem__('head',{})
        super(InterfaceMetaData,self).__setitem__('body',{})
        self.head_set_flag = False
        self.body_set_flag = False


class DataRecorder:

    def __init__(self,cfg):
        self.filename = cfg["filename"]
        self.file = open(self.filename,'wb')

    def record(self,dict):
        pickle.dump(dict,self.file,True)
