from __future__ import division
import urllib
import urllib2
import time
import json
import string
import math
import logging

timestamp = time.strftime('%Y%m%d%H%M',time.localtime(time.time()))
timestampint = string.atoi(timestamp)-1
timestamp = '%d'%timestampint
print ("----- get_discount diff start bizid=3,cityid=88,minute=%s ----"%timestamp)

urlbase = "http://127.0.0.1:8509/canal/get_discount?bizid=3&cityid=88&minute="+timestamp
urltest = "http://127.0.0.1:8508/canal/get_discount?bizid=3&cityid=88&minute="+timestamp

#post base req and recieve resp
reqbase = urllib2.Request(urlbase)
base_resp = urllib2.urlopen(reqbase)
basejson = json.loads(base_resp.read())
basedata = basejson['data']

#post test req and recieve resp
reqtest = urllib2.Request(urltest)
test_resp = urllib2.urlopen(reqtest)
testjson = json.loads(test_resp.read())
testdata = testjson['data']

#compare result
baselen = len(basejson['data'])
testlen = len(testjson['data'])
if(cmp(baselen,testlen)!=0):
    print ('      rply data not matched , testrply data lenth:%d,baserply data lenth:%d'%(testlen,baselen))
else:
    print ('      rply data comlete matched,data lenth:%d'%testlen)
