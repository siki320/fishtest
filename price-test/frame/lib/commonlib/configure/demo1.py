#!/usr/bin/env python
# -*- coding: GB18030 -*-
'''
Created on 2012-3-10

@author: tongdangdang
'''

import os.path
from configarray import *
from configgroup import *
from configunit import *
from configure import *

if __name__ == '__main__':
    conf = Configure()
    conf["LEVEL1"] = configgroup.ConfigGroup("LEVEL1", 1, conf["CONF"])
    conf["LEVEL1"]["LEVEL2"] = configunit.ConfigUnit("LEVEL2", "LEVEL2-VALUE", conf["LEVEL2"])
    conf.load("./test/", "test.conf")
    print conf.conf
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
    """
    conf["GLOBAL"].add(configgroup.ConfigGroup("GLOBAL", 1, conf["GLOBAL"]))  #在数组中新添加一个元素
    print "type if conf['GLOBAL'] = ", type(conf['GLOBAL'])
    print "conf['GLOBAL'].level = ", conf["GLOBAL"].level
    conf["GLOBAL"][3]["dddddd"] = "[][][]"
    conf["GLOBAL"][3]["gggggg"] = configgroup.ConfigGroup("gggggg", 2, conf["GLOBAL"][3])
    conf["GLOBAL"][3]["gggggg"]["rrrrrr"] = "{}{}{}{}"
    conf["GLOBAL"][3]["gggggg"]["rrrrrr"] = "{}{}{}{}[][][]"
    conf["GLOBAL"][3]["Zrray"] = configarray.ConfigArray("ZXXX", -1, conf["GLOBAL"][3])
    conf["GLOBAL"][3]["Zrray"].add(configunit.ConfigUnit("111", "444", conf["GLOBAL"][3]["Zrray"]))
    conf["GLOBAL"][3]["Zrray"].add(configunit.ConfigUnit("111", "444", conf["GLOBAL"][3]["Zrray"]))
    conf["GLOBAL"].add(configgroup.ConfigGroup("GLOBAL", 1, conf["GLOBAL"]))
    conf["GLOBAL"][4]["Zrray"] = configarray.ConfigArray("ZXXX", -1, conf["GLOBAL"][4])
    conf["GLOBAL"][4]["Zrray"].add(configgroup.ConfigGroup("ggggggiiii", 2, conf["GLOBAL"][4]["Zrray"]))
    conf["GLOBAL"][4]["Zrray"][0]["jjjj"] = "ppp"
    conf["GLOBAL"][4]["Zrray"][0]["jjjje"] = "pppoo"
    del conf["GLOBAL"][4]["Zrray"][0]["jjjj"]
    #del conf["GLOBAL"][3]["Zrray"]
    #del conf["GLOBAL"][3]["dddddd"]
    #del conf["GLOBAL"][3]["Zrray"][2]["jjjj"]
    #del conf["GLOBAL"][3]["Zrray"][1]
    #del conf["GLOBAL"][3]["Zrray"][1]
    #print "conf['GLOBAL'][3]['Zrray'][1] = ", conf["GLOBAL"][3]["Zrray"][0]["111"]
    conf["GLOBAL"][1]["TTT"]["CCC"].add(configgroup.ConfigGroup("CCC", 3, conf["GLOBAL"][1]["TTT"]["CCC"]))

    conf["ZXCVB"] = configgroup.ConfigGroup("CCCKuuuuuuuuuuuuKKK", 1, None)

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
    """
    #print conf["GLOBAL"][1]["TTT"]["CCC"][2]
#    print conf.conf["GLOBAL"][1]["key1"]
#    print conf.conf["GLOBAL"][0]["key"]
#    print conf.conf
    conf.dump("./test/test.conf.idl")
