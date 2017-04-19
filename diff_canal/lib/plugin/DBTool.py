#!/usr/bin/python
#coding=utf-8
import sys, os, time, datetime
import logging, redis, memcache
import zookeeper, time, threading

DEFAULT_TIMEOUT = 30000

ZOO_OPEN_ACL_UNSAFE = {"perms":0x1f, "scheme":"world", "id" :"anyone"}
verbose = True
quiet = False

class Redis:

    def __init__(self, context):
        self.context = context
        self.redis_host = context['redis_ip']
        self.redis_port = context['redis_port']
        self.conn = redis.Redis(host=self.redis_host,port=int(self.redis_port))
        self.keylist = []

    def set(self,key,value):
        return self.conn.set(key,value)

    def remove(self, key):
        return self.conn.delete(key)

    def get(self, key):
        return self.conn.get(key)

    def hget(self, key, value):
        return self.conn.hget(key,value)

    def hset(self, key, value, filed):
        return self.conn.hset(key,value,filed)

    def hgetall(self, key):
        return self.conn.hgetall(key)


    def keys(self):
        return self.conn.keys()

    def sadd(self, key, value):
        return self.conn.sadd(key,value)

    def check_key(self,key):
        self.keylist = self.conn.keys()
        if key in self.keylist:
            return True
        else:
            return False

    def smembers(self, key):
        return self.conn.smembers(key)

    def zadd(self, name , key, value):
        return self.conn.zadd(name,key,value)

    def zrange(self, name, score1, score2):
        return self.conn.zrange(name, score1, score2)

    def zrangebyscore(self, name, score1, score2):
        return self.conn.zrangebyscore(name, score1, score2)

    def zscore(self, name, key):
        return self.conn.zscore(name, key)

    def ttl(self, name):
        return self.conn.ttl(name)

    def delete(self,key):
        return self.conn.delete(key)

    def clear(self):
        return self.conn.flushdb()

class Memcached:

    def __init__(self, context):
	self.mc_host = context['ckv_ip']
	self.mc_port = context['ckv_port']
	self.mc_conn = "%s:%s" %(self.mc_host,self.mc_port)
	self.mc0 = memcache.Client([self.mc_conn], debug=0)

    def get(self):
	print "memcache test"
    def clear(self):
	return self.mc0.flush_all()



class ZKClientError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class ZKClient(object):
    def __init__(self, context, timeout=DEFAULT_TIMEOUT):
        self.servers = str(context['zk_ip']) + ':' + str(context['zk_port'])
        self.timeout = timeout
        self.connected = False
        self.conn_cv = threading.Condition( )
        self.handle = -1

        self.conn_cv.acquire()
        if not quiet: print("Connecting to %s" % (self.servers))
        start = time.time()
        self.handle = zookeeper.init(self.servers, self.connection_watcher, timeout)
        self.conn_cv.wait(timeout/1000)
        self.conn_cv.release()

        if not self.connected:
            raise ZKClientError("Unable to connect to %s" % (self.servers))

        if not quiet:
            print("Connected in %d ms, handle is %d"
                  % (int((time.time() - start) * 1000), self.handle))

    def connection_watcher(self, h, type, state, path):
        self.handle = h
        self.conn_cv.acquire()
        self.connected = True
        self.conn_cv.notifyAll()
        self.conn_cv.release()

    def close(self):
        return zookeeper.close(self.handle)

    def create(self, path, data="", flags=0, acl=[ZOO_OPEN_ACL_UNSAFE]):
        start = time.time()
        result = zookeeper.create(self.handle, path, data, acl, flags)
        if verbose:
            print("Node %s created in %d ms"
                  % (path, int((time.time() - start) * 1000)))
        return result

    def delete(self, path, version=-1):
        start = time.time()
        result = zookeeper.delete(self.handle, path, version)
        return result

    def clear(self, path, version=-1, watcher=None):
        self.result = -1
        self.AllNode = self.get_children(path, watcher)
        if self.AllNode != []:
            for node in self.AllNode:
                nodePath = path + '/' + node
                result = self.delete(nodePath, version)
        return self.result

    def check_key(self, node, watcher=None):
        self.AllNode = self.get_children('/', watcher)
        if node in self.AllNode:
              return True
        else:
              return False

    def check_node(self, path, watcher=None):
        self.AllNode = self.get_children(path, watcher)
        if self.AllNode == []:
              return False
        else:
              return True

    def get(self, path, watcher=None):
        return zookeeper.get(self.handle, path, watcher)

    def exists(self, path, watcher=None):
        return zookeeper.exists(self.handle, path, watcher)

    def set(self, path, data="", version=-1):
        return zookeeper.set(self.handle, path, data, version)

    def set2(self, path, data="", version=-1):
        return zookeeper.set2(self.handle, path, data, version)


    def get_children(self, path, watcher=None):
        return zookeeper.get_children(self.handle, path, watcher)

    def async(self, path = "/"):
        return zookeeper.async(self.handle, path)

    def acreate(self, path, callback, data="", flags=0, acl=[ZOO_OPEN_ACL_UNSAFE]):
        result = zookeeper.acreate(self.handle, path, data, acl, flags, callback)
        return result

    def adelete(self, path, callback, version=-1):
        return zookeeper.adelete(self.handle, path, version, callback)

    def aget(self, path, callback, watcher=None):
        return zookeeper.aget(self.handle, path, watcher, callback)

    def aexists(self, path, callback, watcher=None):
        return zookeeper.aexists(self.handle, path, watcher, callback)

    def aset(self, path, callback, data="", version=-1):
        return zookeeper.aset(self.handle, path, data, version, callback)

if __name__ == '__main__':
    context = {}
    context['redis_ip'] = "127.0.0.1"
    context['redis_port'] = "6379"
    context['ckv_ip'] = "127.0.0.1"
    context['ckv_port'] = "11211"
    #test_url = 'http://127.0.0.1:8081/sdp/o_add?id=88&data=3243403028577&source=newOrder&lng=114.025798&lat=22.537872&is_shared=0&order_type=0&sid=gulfstream'
    test_url2 = 'http://127.0.0.1:8081/sdp/o_add?id=88&data=9243403028577&source=newOrder&lng=116.025798&lat=23.537872&is_shared=0&order_type=0&sid=gulfstream'
    r = Redis(context)
    c = SdpTestDriver.CurlDriver()
    #c.setCurl(test_url)
    ret = c.setCurl(test_url2)
    print ret
    r.set('wzy','hahha')
    r.remove('LOCK_DID_1')
    s = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    d = datetime.datetime.strptime(s,'%Y-%m-%d %H:%M:%S')
    createtime = int(time.mktime(d.timetuple()))
    dic = r.hget('SPLIT_ORDER_88')
    test = "114.025798|22.537872|"+str(createtime)+"|0|0"
    print createtime
    print "tttttt",dic.has_key('3243403028577')
    print r.check_key('SPLIT_ORDER_88')
    print r.smembers('sdp_area_set')
    is_name =  "88" in r.smembers('sdp_area_set')
    print is_name
    print r.zadd("wy","name1","1.1")
    print r.zadd("wy","name2","1.2")
    print r.zrange("wy","0", "-1")
    print r.zrangebyscore("wy",1.1,3)
    m = Memcached(context)
    m.get()
