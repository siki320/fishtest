#!/usr/bin/python

import sys
import pycurl
import time
import StringIO
from DBTool import Memcached

from thrift import Thrift
from thrift.Thrift import TException
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

class Thrift:
    def __init__(self,context):
        self.transport=TSocket.TSocket(context['thrift_ip'], int(context['thrift_port']))
        self.transport=TTransport.TFramedTransport(self.transport)
        self.protocol=TBinaryProtocol.TBinaryProtocol(self.transport)
        #client= DuseSchedule.Client(protocol)

    def thriftOpen(self):
        self.transport.open()

    def thriftClose(self):
        self.transport.close()

class Http:

    def __init__(self):
	self.curl = pycurl.Curl()
        self.ret = StringIO.StringIO()

    def setCurl(self, opt):
	try:
	    self.curl.setopt(pycurl.URL, opt)
	    self.curl.setopt(pycurl.WRITEFUNCTION, self.ret.write)
	    self.curl.perform()
	    ret = self.ret.getvalue()
	    self.curl.close()
	    return ret
	except:
	    print "error for set"

    def setPostCurl(self, url, pfield):
	try:
	    self.curl.setopt(pycurl.URL, url)
	    self.curl.setopt(pycurl.POSTFIELDS, pfield)
	    self.curl.setopt(pycurl.WRITEFUNCTION, self.ret.write)
	    self.curl.setopt(pycurl.VERBOSE, False)
	    self.curl.perform()
	    ret = self.ret.getvalue()
	    self.curl.close()
	    return ret
	except:
	    print "error for set"

class StgDriver(Memcached):

    def __init__(self, context):
	Memcached.__init__(self, context)
	self.locFeature = "a:3:{s:3:\"lat\";d:39.928967061245608;s:3:\"lng\";d:116.501826105342417;s:4:\"time\";i:1449455256;}"

    def setDriverDloc(self, did):
	key = "DRIVER_LOC_" + did
	val = self.locFeature
        return self.mc0.set(key, val, 0)

if __name__ == '__main__':
    context = {}
    context['ckv_ip'] = "127.0.0.1"
    context['ckv_port'] = "11211"

    c_url = 'http://127.0.0.1:8081/sdp/o_add?id=1&data=3243403028577&source=newOrder&lng=114.025798&lat=22.537872&is_shared=0&order_type=0&sid=gulfstream'
    c_url2 = 'http://127.0.0.1:8081/sdp/o_add?id=1&data=3243403028537&source=newOrder&lng=114.025798&lat=22.537872&is_shared=0&order_type=0&sid=gulfstream'
    p = CurlDriver()
    print p.setCurl(c_url)
    q = CurlDriver()
    print q.setCurl(c_url2)
    url = "http://127.0.0.1:8081/sdp/d_connect"
    postf = "logid=1111111111111&user_id=562950053421446&type=3&sid=gulfstream"
    s = StgDriver(context)
    s.setDriverDloc("562950053421446")
    y = CurlDriver()
    print y.setPostCurl(url, postf)
