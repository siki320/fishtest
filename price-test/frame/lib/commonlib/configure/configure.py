#!/usr/bin/env python
# -*- coding: GB18030 -*-
'''
Created on 2012-3-10

@author: tongdangdang
'''

import os.path
from configunit import *
from configgroup import *
from configarray import *

_LEAF_NODE_LEVEL = -1

'''
[GLOBAL] level=1
[.LV] level =2
...
key:value level = -1
'''

class Configure(object):
    '''
    @author: tongdangdang
    @summary: configure
    '''
    def __init__(self,sep = ':'):
        self.sep = sep
        self.dir = None
        self.filename = None
        self.conf = configgroup.ConfigGroup("CONF" , 0, None, "", self.sep)
        self.curnode = self.conf
        self.tmp_note = ""
        
    def __setitem__(self,key,value):
        self.conf[key] = value
        
    def __getitem__(self,key):
        return self.conf[key]
        
    def __delitem__(self, key):
        del self.conf[key]
        
    '''
    @summary: format line
    '''
    def _format_line(self,line):
        comment_start = line.find('#') 
        tmp_line = line
        if comment_start>=1:
            tmp_line = line[:comment_start-1]
            self.tmp_note += line[comment_start:]
        return tmp_line.strip()
    
    '''
    @summary: get group name
    @param str: ..@group1
    @return: group1
    '''
    def _get_group_name(self,str):
        #if can not find . rfind return -1 and -1+1=0 is also idx we need
        idx_s1 = str.rfind('.')+1
        idx_s2 = str.rfind('@')+1
        idx_s = idx_s2 and idx_s2 or idx_s1
        return str[idx_s:]
    
    '''
    @summary: check if is group or not
    '''
    def _is_group(self,line):
        return line[0] =='[' and line[-1] == ']'
    
    '''
    @summary: check if is array or not
    '''
    def _is_array(self,line):
        if self._is_group(line):
            return line.find('@') != -1
        else:
            return line[0] == '@'
    
    '''
    @summary: get level
    '''
    def _get_level(self,line):
        if self._is_group(line):
            return line.count('.')+1
        else:
            return _LEAF_NODE_LEVEL
        
    '''
    @summary: deal array
    '''
    def _deal_array(self,line):
        if self.curnode == None:
            self.curnode = configarray.ConfigArray(sep = self.sep)
        
    '''
    @summary: deal group 
    '''
    def _deal_group(self,line):
        groupname = self._get_group_name(line[1:-1])
        level = self._get_level(line)
        if self._is_array(line):
            if self.curnode.level == level - 1:
                self.curnode[groupname] = configarray.ConfigArray(groupname, level, self.curnode, sep = self.sep)
                self.curnode = self.curnode[groupname]
                self.curnode.add(configgroup.ConfigGroup(groupname, level, self.curnode, self.tmp_note, self.sep))
                self.curnode = self.curnode[0]
            elif groupname == self.curnode.name and level == self.curnode.level:
                self.curnode.father.add(configgroup.ConfigGroup(groupname, level, self.curnode.father, self.tmp_note, self.sep))
                self.curnode = self.curnode.father[-1]
            elif groupname != self.curnode.name and level == self.curnode.level:
                if isinstance(self.curnode.father,configarray.ConfigArray):
                    self.curnode = self.curnode.father.father
                else:
                    self.curnode = self.curnode.father
                self.curnode[groupname] = configarray.ConfigArray(groupname, level, self.curnode, sep = self.sep)
                self.curnode = self.curnode[groupname]
                self.curnode.add(configgroup.ConfigGroup(groupname, level, self.curnode, self.tmp_note, self.sep))
                self.curnode = self.curnode[0]
            elif self.curnode.level > level or self.curnode.level == -1:
                if self.curnode.level == -1:
                    self.curnode = self.curnode.father
                l = self.curnode.level -level
                for i in range(l+1):
                    self.curnode = self.curnode.father
                    if isinstance(self.curnode, configarray.ConfigArray):
                        self.curnode = self.curnode.father
                if self.curnode[groupname] == None:
                    self.curnode[groupname] = configarray.ConfigArray(groupname, level, self.curnode, sep = self.sep)
                    self.curnode = self.curnode[groupname]
                    self.curnode.add(configgroup.ConfigGroup(groupname, level, self.curnode, self.tmp_note, self.sep))
                    self.curnode = self.curnode[0]
                else:
                    self.curnode[groupname].add(configgroup.ConfigGroup(groupname, level, self.curnode[groupname], self.tmp_note, self.sep))
                    self.curnode = self.curnode[groupname][-1]
        else:
            if self.curnode.level == level - 1:
                self.curnode[groupname] = configgroup.ConfigGroup(groupname, level, self.curnode, self.tmp_note, self.sep)
                self.curnode = self.curnode[groupname]
            elif groupname != self.curnode.name and level == self.curnode.level:
                if isinstance(self.curnode.father,configarray.ConfigArray):
                    self.curnode = self.curnode.father.father
                else:
                    self.curnode = self.curnode.father
                self.curnode[groupname] = configgroup.ConfigGroup(groupname, level, self.curnode, self.tmp_note, self.sep)
                self.curnode = self.curnode[groupname]
            elif (self.curnode.level > level) or self.curnode.level == -1:
                if self.curnode.level == -1:
                    self.curnode = self.curnode.father
                l = self.curnode.level -level
                for i in range(l+1):
                    self.curnode = self.curnode.father
                    if isinstance(self.curnode, configarray.ConfigArray):
                        self.curnode = self.curnode.father
                if self.curnode[groupname] == None:
                    self.curnode[groupname] = configgroup.ConfigGroup(groupname, level, self.curnode, self.tmp_note, self.sep)
                    self.curnode = self.curnode[groupname]
                else:
                    self.curnode[groupname].add(configgroup.ConfigGroup(groupname, level, self.curnode[groupname], self.tmp_note, self.sep))
                    self.curnode = self.curnode[groupname][-1]
                
             
    '''
    @summary: deal unit
    '''
    def _deal_unit(self,line):
        key,value = [str.strip() for str in line.split(self.sep, 1)]
        #get key name can also use _get_group_name
        key = self._get_group_name(key)
        level = _LEAF_NODE_LEVEL
        if self._is_array(line):
            if self.curnode.level == _LEAF_NODE_LEVEL and self.curnode.name == key:
                self.curnode.add(configunit.ConfigUnit(key,value,self.curnode,self.tmp_note))
            elif self.curnode.level == _LEAF_NODE_LEVEL and self.curnode.name != key:
                if self.curnode.father[key] == None:
                    self.curnode.father[key] = configarray.ConfigArray(key, level, self.curnode.father, sep = self.sep)
                    self.curnode = self.curnode.father[key]
                    self.curnode.add(configunit.ConfigUnit(key, value, self.curnode, self.tmp_note))
                else:
                    self.curnode.father[key].add(configunit.ConfigUnit(key, value, self.curnode.father, self.tmp_note))
                    self.curnode = self.curnode.father[key]
            elif self.curnode.level != _LEAF_NODE_LEVEL:
                self.curnode[key] = configarray.ConfigArray(key, level, self.curnode, sep = self.sep)
                self.curnode = self.curnode[key]
                self.curnode.add(configunit.ConfigUnit(key, value, self.curnode, self.tmp_note))
        else:
            if self.curnode.level == _LEAF_NODE_LEVEL:
                self.curnode.father[key] = configunit.ConfigUnit(key, value, self.curnode, self.tmp_note)
                self.curnode = self.curnode.father
            else:
                self.curnode[key] = configunit.ConfigUnit(key, value, self.curnode, self.tmp_note)
            

    '''
    @summary: deal one line
    '''
    def _deal_one_line(self,line_orig):
        line = self._format_line(line_orig)
        if len(line) == 0 or line[0] == '#':
            self.tmp_note +=line_orig
        elif self._is_group(line):
            self._deal_group(line)
            self.tmp_note = ""
        else:
            self._deal_unit(line)
            self.tmp_note = ""
            
            
        
    '''
    @summary: load conf from file
    '''
    def load(self, dir, filename):
        self.dir = dir
        self.filename = filename
        if os.path.exists(os.path.join(dir, filename)):
            f = open(os.path.join(dir,filename))
            for line in f:
                self._deal_one_line(line)
        else:
            raise AssertionError,"filepath:[%s/%s] does not exist!" % (dir,filename)
        f.close()
                
    '''
    @summary: dump
    '''
    def dump(self, filepath = None):
        if filepath == None:
            filepath = self.dir + "/" + self.filename
        _file = open(filepath,'w')
        print >> _file,str(self.conf)[7:-1]
        _file.close()
                
    def delete(self, deletepath):
        if deletepath == None:
            return True
        if type(deletepath) in [configunit.ConfigUnit, configarray.ConfigArray, configgroup.ConfigGroup]:
            del deletepath

if __name__ == '__main__':
    conf = Configure()
    conf.load("./test/", "test.conf")
#    print conf.conf
#    print conf.conf["GLOBAL"][1]
    #conf["GLOBAL"][0]["key"] = "ttsss"
    #conf["GLOBAL"][1]["TTT"]["key"] = "wawa"
    #conf["GLOBAL"][1]["TTT"]["key1"] = "wawa"
    #conf["GLOBAL"][1]["UUU"] =  configgroup.ConfigGroup("UUU",2,conf.conf["GLOBAL"][1])
    #conf["GLOBAL"][1]["UUU"]["keyy"] = "uuuuu"
    #conf["GLOBAL"].add(configgroup.ConfigGroup("GLOBAL",1,conf.conf["GLOBAL"]))
    #conf["GLOBAL"][2]["kkk"] = "oooooooooo"
    #conf["GLOBAL"][2]["PPPP"] = configgroup.ConfigGroup("AAAAAA",2,conf.conf["GLOBAL"][2])
    #conf["GLOBAL"][2]["PPPP"]["QQQQ"] = "bbbbbbbbbbbbbb"
    #conf["GLOBAL"][2]["CCCCC"] = configarray.ConfigArray("XXXX", 2, conf["GLOBAL"][2])
    #conf["GLOBAL"][2]["CCCCC"].add(configunit.ConfigUnit("222", "333", conf["GLOBAL"][2]))
    #conf["GLOBAL"][2]["CCCCC"].add(configunit.ConfigUnit("222", "333", conf["GLOBAL"][2]))
    #conf["GLOBAL"][2]["AAAAAA"]["222"].add(configunit.ConfigUnit("222", "34433", conf["GLOBAL"][2]))
    #print conf.conf["GLOBAL"][1]
    #conf["GLOBAL"][1]["TTT"].__setitem__("CCC", configarray.ConfigArray("CCC",2,conf["GLOBAL"][1]["TTT"]))
    #conf["GLOBAL"][1]["TTT"]["CCC"].add(configunit.ConfigUnit("222", "333", conf["GLOBAL"][1]["TTT"]["CCC"]))
    #conf["GLOBAL"][1]["TTT"]["CCC"].add(configunit.ConfigUnit("eeeeeeee", "qqqqqqqqq", conf["GLOBAL"][1]["TTT"]["CCC"]))
    #conf["GLOBAL"][2].add(configgroup.ConfigGroup("GLOBAL",0,conf.conf,"#lady gagaiiiiiiiiiiiiiii\n"))
    
    conf["GLOBAL"].add(configgroup.ConfigGroup("GLOBAL", 1, conf["GLOBAL"], "", conf.sep))#在数组中新添加一个元素
    print "type if conf['GLOBAL'] = ", type(conf['GLOBAL'])
    print "conf['GLOBAL'].level = ", conf["GLOBAL"].level
    conf["GLOBAL"][3]["dddddd"] = "[][][]"
    conf["GLOBAL"][3]["gggggg"] = configgroup.ConfigGroup("gggggg", 2, conf["GLOBAL"][3], "", conf.sep)
    conf["GLOBAL"][3]["gggggg"]["rrrrrr"] = "{}{}{}{}"
    conf["GLOBAL"][3]["gggggg"]["rrrrrr"] = "{}{}{}{}[][][]"
    conf["GLOBAL"][3]["Zrray"] = configarray.ConfigArray("ZXXX", -1, conf["GLOBAL"][3], conf.sep)
    conf["GLOBAL"][3]["Zrray"].add(configunit.ConfigUnit("111", "444", conf["GLOBAL"][3]["Zrray"]))
    conf["GLOBAL"][3]["Zrray"].add(configunit.ConfigUnit("111", "444", conf["GLOBAL"][3]["Zrray"]))
    conf["GLOBAL"].add(configgroup.ConfigGroup("GLOBAL", 1, conf["GLOBAL"], "", conf.sep))
    conf["GLOBAL"][4]["Zrray"] = configarray.ConfigArray("ZXXX", -1, conf["GLOBAL"][4], conf.sep)
    conf["GLOBAL"][4]["Zrray"].add(configgroup.ConfigGroup("ggggggiiii", 2, conf["GLOBAL"][4]["Zrray"], "", conf.sep))
    conf["GLOBAL"][4]["Zrray"][0]["jjjj"] = "ppp"
    conf["GLOBAL"][4]["Zrray"][0]["jjjje"] = "pppoo"
    del conf["GLOBAL"][4]["Zrray"][0]["jjjj"]
    #del conf["GLOBAL"][3]["Zrray"]
    #del conf["GLOBAL"][3]["dddddd"]
    #del conf["GLOBAL"][3]["Zrray"][2]["jjjj"]
    #del conf["GLOBAL"][3]["Zrray"][1]
    #del conf["GLOBAL"][3]["Zrray"][1]
    #print "conf['GLOBAL'][3]['Zrray'][1] = ", conf["GLOBAL"][3]["Zrray"][0]["111"]
    conf["GLOBAL"][1]["TTT"]["CCC"].add(configgroup.ConfigGroup("CCC", 3, conf["GLOBAL"][1]["TTT"]["CCC"],"",  conf.sep))

    conf["ZXCVB"] = configgroup.ConfigGroup("CCCKuuuuuuuuuuuuKKK", 1, None, "", conf.sep)

    print "+++++++++++++++++++++++++++++++++++++++"
    print conf["CCCKKKK"]
    print "+++++++++++++++++++++++++++++++++++++++"
    #conf.__setitem__("ZXCVB2", configgroup.ConfigGroup("CCCKKKK", 1, None))
    #conf["ZXCVB2"]["GGGGGGGGGG"] = "LLLLLLLLLLLLL"
    #conf["GLOBAL"][0]["kk"][0] = "klllll"
    print "------------------"
    print conf["GLOBAL"][0]
    print "------------------"
    print conf["GLOBAL"][1]
    print "------------------"
    print conf["GLOBAL"][2]
    print "------------------"
    print conf["GLOBAL"][3]
    print "------------------"
    print conf["GLOBAL"][4]
    print conf["GLOBAL"][1].get_key_dict()
    #print conf["GLOBAL"][1]["TTT"]["CCC"][2]
#    print conf.conf["GLOBAL"][1]["key1"]
#    print conf.conf["GLOBAL"][0]["key"]
#    print conf.conf
    #conf["port"] = "11111111111"
    #conf["NEW"] = configunit.ConfigUnit("NEW", "444", conf["CONF"])
    conf.dump("./test/test.conf.idl")
