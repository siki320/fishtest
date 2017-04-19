from __future__ import division
import urllib
import urllib2
import time
import json
import string
import sys

timestamp = time.strftime('%Y%m%d%H%M',time.localtime(time.time()))
timestampint = string.atoi(timestamp)-1
timestamp = '%d'%timestampint
urlbase = "http://127.0.0.1:8509/canal/get_timeinfo?bizid=1&citylist=1&minute="+timestamp
urltest = "http://127.0.0.1:8508/canal/get_timeinfo?bizid=1&citylist=1&minute="+timestamp

print ("---- get_timeinfo test diff bizid=1,cityid=1,minute=%s ----"%timestamp)

#post base req and recieve resp
reqbase = urllib2.Request(urlbase)
base_resp = urllib2.urlopen(reqbase)
basejson = json.loads(base_resp.read())
if (basejson['errno']!=0 ):
    print ("reply msg error : %s" %basejson)
    sys.exit(1)
base = basejson['data']
basedata = base["1"]["productfeature"]["1"]
baseresult = [basedata['waitingnum'],basedata['waitingtimesum'],basedata['cancelednum'],basedata['canceledtimesum'],basedata['strivednum'],basedata['strivedtimesum'],basedata['totalnum']]

#post test req and recieve resp
reqtest = urllib2.Request(urltest)
test_resp = urllib2.urlopen(reqtest)
testjson = json.loads(test_resp.read())
if (testjson['errno']!=0 ):
    print ("reply msg error : %s" %testjson)
    sys.exit(1)
test = testjson['data']
testdata =  test["1"]["productfeature"]["1"]
testresult = [testdata['waitingnum'],testdata['waitingtimesum'],testdata['cancelednum'],testdata['canceledtimesum'],testdata['strivednum'],testdata['strivedtimesum'],testdata['totalnum']]

#print result
print ("waiting,waittime,cancel,canceltime,strive,strivetime,total")
print ("master rply data %s"%baseresult)
print ("test rply data %s"%testresult)

#compare result
if(cmp(testresult,baseresult)==0):
    print ('     reply data complete match')
else:
    for i in range(0,7):
        if((0.9 < testresult[i]/baseresult[i] < 1.1) and (testresult[i] !=baseresult[i])):
            print("     reply data not complete match,testdata: %s,basedata: %s"%(testresult[i],baseresult[i]))
        elif(testresult[i] != baseresult[i] ):
            print("     reply data error,testdata:%s,basedata:%s"%(testresult[i],baseresult[i]))

