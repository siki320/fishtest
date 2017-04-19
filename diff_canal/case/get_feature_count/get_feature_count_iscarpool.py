from __future__ import division
import urllib
import urllib2
import time
import json
import string
import sys
import math

timestamp = time.strftime('%Y%m%d%H%M',time.localtime(time.time()))
timestampint = string.atoi(timestamp)-1
timestamp = '%d'%timestampint
urlbase = "http://127.0.0.1:8509/canal/get_feature_count?bizid=3&citylist=1&minute="+timestamp+"&iscarpool=1&dpnormal=1"
urltest = "http://127.0.0.1:8508/canal/get_feature_count?bizid=3&citylist=1&minute="+timestamp+"&iscarpool=1&dpnormal=1"

print ("--get_feature_count_iscarpool diff start bizid=3,cityid=1,minute=%s--"%timestamp)

#post base req and recieve resp
reqbase = urllib2.Request(urlbase)
base_resp = urllib2.urlopen(reqbase)
basejson = json.loads(base_resp.read())
if (basejson['errno']!=0 ):
    print ("reply msg error : %s" %basejson)
    sys.exit(1)
base = basejson['data']
basedata = base["1"]["productfeature"]["3"]
baseresult = [basedata['driver_online_service_num'],basedata['driver_online_total_num'],basedata['driver_online_free_num'],basedata['realtime_order_call_num'],basedata['realtime_order_answer_rate'],basedata['realtime_order_strive_num'],basedata['realtime_order_deal_num'],basedata['dynamic_price_total_request']]

#post test req and recieve resp
reqtest = urllib2.Request(urltest)
test_resp = urllib2.urlopen(reqtest)
testjson = json.loads(test_resp.read())
if (testjson['errno']!=0 ):
    print ("reply msg error : %s" %testjson)
    sys.exit(1)
test = testjson['data']
testdata =  test["1"]["productfeature"]["3"]
testresult = [testdata['driver_online_service_num'],testdata['driver_online_total_num'],testdata['driver_online_free_num'],testdata['realtime_order_call_num'],testdata['realtime_order_answer_rate'],testdata['realtime_order_strive_num'],testdata['realtime_order_deal_num'],testdata['dynamic_price_total_request']]

#print result
print ("dr_onserve,dr_online,dr_onfree,order,answer_rate,strive,deal,dynamic_req")
print ("master rply data %s"%baseresult)
print ("test rply data %s"%testresult)
#compare result
if(cmp(testresult,baseresult)==0):
    print ('     reply data complete match')
else:
    for i in range(0,8):
        if((0.9 < testresult[i]/baseresult[i] < 1.1) and (testresult[i] !=baseresult[i])):
            print("     reply data not complete match,testdata: %s,basedata: %s"%(testresult[i],baseresult[i]))
        elif(testresult[i] != baseresult[i]):
            print("     reply data error,testdata:%s,basedata:%s"%(testresult[i],baseresult[i]))


