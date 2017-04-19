#!/usr/bin/python
# -*- coding: utf-8 -*-
#---------------------------------
# @author: zhaoyonghua
# @desc  : common functions for DB operations
#---------------------------------
# when        who          what
#---------------------------------
# 05/07/2014  zhaoyonghua  Create

import ConfigParser
import string, os, sys, re
import logging

#Read Server.conf and return hash
def ReadServerConf(conf=None):
    if conf is None:
        conf = os.path.realpath(sys.path[0]) + "/../conf/Server.conf"
        if not os.path.exists(conf):
            conf = os.path.realpath(sys.path[0]) + "/conf/Server.conf"
    return ReadConf(conf)


#Read config file and return hash
def ReadConf(conf):
    if not os.path.exists(conf):
        logging.warning( "The specified %s doesn't exist." % conf )
        return False

    cfg_dic={}
    cf = ConfigParser.ConfigParser()
    cf.read(conf)
    s = cf.sections()
    for k1 in s:
        o = cf.options(k1)
        cfg_dic[k1]={}
        for k2 in o:
            #if re.match("port", k2) or re.match("lajp", k2):
            #    val = cf.getint(k1, k2)
            #else:
            val = cf.get(k1, k2)
            print k1, k2, val
            if k2.find("port")<0:
                 cfg_dic[k1][k2]=val
            else:
                 cfg_dic[k1][k2]=int(val)

    return cfg_dic

#Debug code
"""
if __name__ == "__main__":
    ReadServerConf()
"""
