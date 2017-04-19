# -*- coding: GB18030 -*-
'''
Created on April 1, 2012

@author: liqiuhua
@modify: geshijing
增加unit维度，每个unit为长度为N的一组端口
一个seg为一组unit的集合，seg通过增加unit自适应所需的端口总数
@summary: port allocation module
'''
import socket
import threading

class PortAlloc(object):
    """ port allcation and manage class"""
    def __init__(self,start, end, unit_len=10):
        self.__port_start = start       # start allocation port number, contained
        self.__port_end = end           # end allcation port number, *NOT* contained
        if unit_len<=1:
            raise Exception,"unit_len must bigger than 1"
        self.__port_unit_len = unit_len # ports num of one port unit
        self.__port_sock = {}           # <unit head port, the socket objects of the head port allocated> dict
        self.__port_seg_start = {}      # <segment head port, list of unit head ports> dict
        self.mutex = threading.Lock()
        self.__free_ports = {}          # <the free ports of each segment
        self.debug_ports = self.__free_ports
        self.__use_ports = {}          # <the free ports of each segment
        self.debug_ports1 = self.__use_ports          # <the free ports of each segment
        self.__temp_seg_port = None  # for allocating port temporarily

    def allocPortSeg(self):
        """
        @summary: alloc one port segment
        @retval: return the start port of the port segment
        """
        self.mutex.acquire() #获取互斥锁
        try:
            seg_start = self.__allocPortUnit()
            self.__free_ports[seg_start] = range(seg_start+1, seg_start+self.__port_unit_len)
            self.__use_ports[seg_start] = []
        finally:
            self.mutex.release() #释放互斥锁
        return seg_start

    def freePortSeg(self,seg_start):
        """
        @desc free the port segment
        """
        if not self.__port_seg_start.has_key(seg_start):
            raise Exception,"the port segment:%d is not allocated!"%seg_start
        self.mutex.acquire() #获取互斥锁
        for port in self.__port_seg_start[seg_start]:
            self.__port_sock[port].close()
        del self.__port_seg_start[seg_start]
        self.__free_ports[seg_start] = []
        self.__use_ports[seg_start] = []
        self.mutex.release() #释放互斥锁

    def __allocPortUnit(self,seg_start= None):
        """
        @summary: alloc one port unit,warning this method is not muti-thread safe,get lock before using it
        @retval: return the start port of the port segment
        """
        sock = socket.socket()
        cur_port = self.__port_start
        while cur_port + self.__port_unit_len <= self.__port_end:    # 还足够分配一个segment，循环继续
            if cur_port in self.__port_sock.keys():
                # 已经分配过，跳过
                cur_port += self.__port_unit_len
                continue
            try:
                sock.bind(('', cur_port))
                sock.listen(1)      # listen后，port会出现在netstat -ln中
            except Exception:
                # 不能bind，跳过
                cur_port += self.__port_unit_len
                continue

            # cur_port绑定成功
            self.__port_sock[cur_port] = sock
            if seg_start and self.__port_seg_start.has_key(seg_start):
                #当前申请为一个已有的segs 申请新的seg
                pass
                self.__port_seg_start[seg_start].append(cur_port)
            else:
                #当前的申请为一个全新的segs
                seg_start = cur_port
                self.__port_seg_start[seg_start] =[cur_port]
            return cur_port

        # 未能找到可用的head port
        sock.close()
        raise Exception, "allocPortSeg failed. No usable segment head port"

    def freePortSeg(self,seg_start):
        """
        @desc free the port segment
        """
        if not self.__port_seg_start.has_key(seg_start):
            raise Exception,"the port segment:%d is not allocated!"%seg_start
        self.mutex.acquire() #获取互斥锁
        for port in self.__port_seg_start[seg_start]:
            self.__port_sock[port].close()
        del self.__port_seg_start[seg_start]
        self.mutex.release() #释放互斥锁

    def allocPort(self, seg_start=None):
        """
        @desc: alloc an available port from the port segment
        @retval: return an available port
        """
        if seg_start and not self.__port_seg_start.has_key(seg_start):
            raise Exception,"the port segment:%d is not allocated!"%seg_start
        if not seg_start:
            # for allocating port temporarily 
            if not self.__temp_seg_port: 
                self.__temp_seg_port = self.allocPortSeg()
            seg_start = self.__temp_seg_port

        sock = socket.socket()
        self.mutex.acquire() #获取互斥锁
        use_port = None
        try:
            while use_port==None:
                for use_port in self.__free_ports[seg_start]:
                    try:
                        sock.bind(('',use_port))
                        break
                    except:
                        use_port = None
                        continue
                if use_port==None:
                    #current unit has no available port. get idl one
                    new_seg_start=self.__allocPortUnit(seg_start) 
                    free_ports = range(new_seg_start+1, new_seg_start+self.__port_unit_len)
                    self.__free_ports[seg_start].extend(free_ports)
            sock.close()
            self.__free_ports[seg_start].remove(use_port)
            self.__use_ports[seg_start].append(use_port)
        finally:
            self.mutex.release() #释放互斥锁
        return use_port

    def freePort(self, use_port):
        """
        @desc: free the port
        """
        self.mutex.acquire() #获取互斥锁
        for seg_start in self.__use_ports:
            if use_port in self.__use_ports[seg_start]:
                self.__use_ports[seg_start].remove(use_port)
                self.__free_ports[seg_start].append(use_port)
        self.mutex.release() #释放互斥锁
        return use_port


#全局分配器, 端口区间为: (ip_local_port_range最大端口+100)~65500, 每个segment有100个端口
#默认起始端口号为61100
begin_port = 61100
end_port   = 65500
try:
    port_range_file = file("/proc/sys/net/ipv4/ip_local_port_range")
    port_range_str = port_range_file.readline()
    port_range_file.close()
    tmp_list = port_range_str.split("\t")
    begin_port = int(tmp_list[1].rstrip())+100
except:
    begin_port = 61100

if begin_port<=1024:
    begin_port = 61100

portalloc = PortAlloc(begin_port, end_port, 100)

def _test():
    # 全局portalloc使用法
    print "Global portalloc usage. port rage : %d, %d, 100" % (begin_port, end_port)
    # 临时直接分配一个端口
    print "temp allocation:",portalloc.allocPort()
    segport = portalloc.allocPortSeg()
    print "segport:", segport
    print "first alloc:", portalloc.allocPort(segport)
    second = portalloc.allocPort(segport)
    print "second alloc:", second
    print "second free:", portalloc.freePort(second)
    print "third alloc:", portalloc.allocPort(segport)
    portalloc.freePortSeg(segport)

    # 分配segment直到失败
    print
    print "Alloc segment untill fail. port range : 61234, 61242(61243), 3"
    pa = PortAlloc(61234, 61242, 3)
    seg1 = pa.allocPortSeg()
    print "segport1:", seg1
    seg2 = pa.allocPortSeg()
    print "segport2:", seg2
    try:
        pa.allocPortSeg()
    except Exception, e:
        print "segport3:", e

    pa2 = PortAlloc(61234, 61243, 3)
    seg3 = pa2.allocPortSeg()
    print "segport3:", seg3
    print "port alloc1:",pa2.allocPort(seg3)
    temp = pa2.allocPort(seg3)
    print "port alloc2:",temp
    print "port free:",pa2.freePort(temp)
    print "port alloc3:",pa2.allocPort(seg3)

    pa.freePortSeg(seg1)
    pa.freePortSeg(seg2)
    pa2.freePortSeg(seg3)

    # 分配port直到失败
    print
    print "Alloc port untill a idl unit is alloced, port range : 61234, 61342, 3"
    pa = PortAlloc(61234, 61342, 3)
    segport = pa.allocPortSeg()
    print "segport:", segport
    for i in range (0,100):
        port = pa.allocPort(segport)
        print "%dth try, get port %d"%(i+1,port)
    pa.freePortSeg(segport)
if __name__ == "__main__":
    _test()

