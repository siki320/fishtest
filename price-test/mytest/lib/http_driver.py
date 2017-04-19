# -*- coding: utf-8 -*-
#!/usr/bin/env python

import httplib
import json

import urllib
import urllib2


class httpdriver(object):
    def __init__(self,ip,port):
        self.ip = ip
        self.port = port
        pass
        
    def HTTPGet(self,url):
        conn=httplib.HTTPConnection(self.ip,self.port)
        conn.request('GET',url)
        res=conn.getresponse()
        res=res.read()
        conn.close()
        return res
        
    def HTTPPost(self,url="", p_data={}):
        url="http://%s:%s%s"%(self.ip,self.port,url)
        print url
        jdata = json.dumps(p_data) # 对数据进行JSON格式化编码
        req = urllib2.Request(url, jdata)
        print jdata
        response = urllib2.urlopen(req) 
        return json.loads(response.read())

if __name__=='__main__':
    usr=httpdriver()
