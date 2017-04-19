#!/usr/bin/python
# -*- coding: utf-8 -*-
#---------------------------------

import ConfigParser
import string, os, sys, re
import logging

#Read Server.conf and return hash
def ReadServerConf(conf=None):
    if conf is None:
        conf = os.path.realpath(sys.path[0]) + "/../../conf/Server.conf"
        if not os.path.exists(conf):
            conf = os.path.realpath(sys.path[0]) + "/conf/Server.conf"
	    if not os.path.exists(conf):
		conf = os.path.realpath(sys.path[0]) + "/../conf/Server.conf"
        return ReadConf(conf)

def ReadLogConf(conf=None):
    if conf is None:
        conf = os.path.realpath(sys.path[0]) + "/../../conf/log_parser.conf"
        if not os.path.exists(conf):
            conf = os.path.realpath(sys.path[0]) + "/conf/log_parser.conf"
	    if not os.path.exists(conf):
		conf = os.path.realpath(sys.path[0]) + "/../conf/log_parser.conf"
        return ReadConf(conf)

def ReadEnvConf(conf=None):
    if conf is None:
        conf = os.path.realpath(sys.path[0]) + "/../../conf/strategy.conf"
        if not os.path.exists(conf):
            conf = os.path.realpath(sys.path[0]) + "/conf/strategy.conf"
	    if not os.path.exists(conf):
		conf = os.path.realpath(sys.path[0]) + "/../conf/strategy.conf"
    idMap = {}
    execfile(conf)
    return idMap

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
            val = cf.get(k1, k2)
            #print k1, k2, val
            cfg_dic[k1][k2]=val

    return cfg_dic
def init():
        cfg=ReadServerConf()
        context = {}
#        context['env'] = cfg["stg"]["env"]

        context['ckv_ip'] = cfg["ckv0"]["ckv_host"]
        context['ckv_port'] = cfg["ckv0"]["ckv_port"]
        context['nginx_ip'] = cfg["id_server0"]["id_host"]
        context['nginx_port'] =cfg["id_server0"]["id_port"]
        context['redis_ip'] = cfg["redis0"]["rds_host"]
        context['redis_port'] = cfg["redis0"]["rds_port"]
	context['redis_ip1'] = cfg["redis1"]["rds_host"]
        context['redis_port1'] = cfg["redis1"]["rds_port"]
        context['zk_ip'] = cfg["zk0"]["zk_host"]
        context['zk_port'] = cfg["zk0"]["zk_port"]
        context['thrift_ip'] = cfg["thrift_server0"]["id_host"]
        context['thrift_port'] = cfg["thrift_server0"]["id_port"]
        context['http_ip'] = cfg["http_server0"]["id_host"]
        context['http_port'] = cfg["http_server0"]["id_port"]

#        context['input_driver_file'] = cfg["data_input"]["input_driver_file"]
#        context['input_driver_loc_file'] = cfg["data_input"]["input_driver_loc_file"]
        return context
#Debug code

if __name__ == "__main__":
    dict = ReadEnvConf()
    #print dict['stg']
