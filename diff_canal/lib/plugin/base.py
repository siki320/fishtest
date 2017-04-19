#!/usr/bin/python
#coding=utf-8
import sys, os, time, datetime
import json
from collections import OrderedDict


def get_createtime():
    nowtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    transtime = datetime.datetime.strptime(nowtime,'%Y-%m-%d %H:%M:%S')
    return int(time.mktime(transtime.timetuple()))

def get_mscreatetime():
    nowtime = int(round(time.time() * 1000))
    return nowtime

def fmtOutInput(paraIn):
    print
    dict = {}
    if type(paraIn) == str:
    	print "Para input = %s" % (paraIn)
    elif type(paraIn) == type(dict):
	for i in paraIn:
	    print "Para input = %s,%s" %(i, paraIn[i])

def fmtOutOutput(name, paraOut):
    print
    dict = {}
    if type(paraOut) == str:
        print "Para output : %s = %s" % (name, paraOut)
    elif type(paraOut) == type(dict):
        for i in paraOut:
            print "Para output %s = %s,%s" %(name, i, paraOut[i])

def stripSpace(s):
    return str(s).replace(' ','')

def Time2String(s):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(s)/1000))

def String2Time(s):
    return time.mktime(time.strptime(s,"%Y-%m-%d %H:%M:%S"))

def timeTransfer(input):
    jret = json.loads(input,object_pairs_hook=OrderedDict)
    dt = jret['timestamp']
    st = Time2String(dt)
    mtime = str(int(String2Time(st)))
    jret['timestamp'] = mtime
    if jret['id'] != -1 :
       jret['jobid'] = mtime
    return stripSpace(json.dumps(jret))

def get_res_time(input):
    jret = json.loads(input)
    return jret['timestamp']

if __name__ == '__main__':
    print get_createtime()
    dict = {"wzy":123,"www":3234}
    s = "212121"
    fmtOutOutput("test",dict)
    tmp = '{"errno":0,"errmsg":"ok","order_id":"3243403028577","shared_order_id":"","driver_id":"562950053421446","id":1,"timestamp":"1453182796123","jobid":"1453182796123","seqid":"1"}'
    timeTransfer(tmp)
