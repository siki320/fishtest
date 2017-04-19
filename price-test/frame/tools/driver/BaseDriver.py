# -*- coding: GB18030 -*-
# '''
# Created on Dec 11, 2011
# @author: maqi<maqi>
# @summary: dts base driver
# '''

import socket,threading
from frame.lib.commonlib.dlog import dlog
from frame.tools.lib.core import InterfaceMetaData

class BaseDriver(object):

    def __init__(self, cfg):
        self.port = int(cfg.get("port",12345))
        self.ip = cfg.get("ip","127.0.0.1")
        self.name = cfg.get("name","base_driver")
        #self.verbose = cfg.get("verbose",1)
        self.rdtmout = cfg.get("readtimeout",0.2)
        self.wrtmout = cfg.get("writetimeout",0.2)
        self.cntmout = cfg.get("connecttimeout",0.2)
        self.conntype = cfg.get("conntype",0) #0 短连接，1 长连接

        self.net = DriverNetLib(self)
        self.req = InterfaceMetaData()
        self.res = InterfaceMetaData()
        self.raw_req = None
        self.raw_res = None

    def decode(self,data):
        self.raw_res = data
        self.res.clear()
        self.res["head"],self.res["body"] = self.decoder.decode(data)

    def encode(self):
        if self.raw_req != None:
            return self.raw_req

        if self.req.body_set_flag == False:
            raise RuntimeError,'request body must set'
        elif self.req.head_set_flag == False:
            self.req["head"] = self.encoder.headEncoder.getDefaultHead()

        return self.encoder.encode(self.req["head"],self.req["body"])

    def doEncode(self):
        rawdata = self.encode()
        prefix = "\n" + "\033[4;31m" + "+"*10 + " [IN DRIVER] : " + self.name.upper() + " [REQUEST] " + "+"*10 + "\033[0m"
        logstr = prefix + str(self.req)
        dlog.debug(logstr)

        return rawdata

    def doDecode(self,data):
        self.decode(data)

        prefix = "\n" + "\033[4;31m" + "+"*10 + " [IN DRIVER] : " + self.name.upper() + " [RESPONSE] " + "+"*10 + "\033[0m"
        logstr = prefix + str(self.res)
        dlog.debug(logstr)

    def doRequest(self):
        self.net.invite()

    def clear(self):
        self.req.clear()
        self.res.clear()
        self.raw_req = None
        self.raw_res = None

    def setRequestHead(self,head):
        self.req["head"] = head

    def setRequestBody(self,body):
        self.req["body"] = body


class DriverNetLib():

    def __init__(self, driver):
        self.driver = driver
        self.sockets = []
        self.socket_num = 0
        self.sockcond = threading.Condition()

    def __connect(self):
        try:
            sock = socket.create_connection((self.driver.ip, self.driver.port), self.driver.cntmout)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except socket.error, why:
            dlog.warning("driver connect error (%s), ip(%s), port(%d)", why, self.driver.ip , self.driver.port)
            return None
        return sock

    def __get_socket(self):
        self.sockcond.acquire()
        if len(self.sockets) == 0:
            sock = self.__connect()
            if sock: self.socket_num += 1
        else:
            sock = self.sockets.pop(0)
        self.sockcond.release()
        return sock

    def __put_socket(self, sock):
        self.sockcond.acquire()
        if not sock:
            self.socket_num -= 1
        elif self.driver.conntype:
            self.sockets.append(sock)
        else:
            sock.close()
            self.socket_num -= 1
        self.sockcond.notify()
        self.sockcond.release()

    def invite(self):
        #get socket
        sock = self.__get_socket()
        if not sock:
            dlog.warning("driver connect failed")
            return
        try:
            #send
            reqRawData = self.driver.doEncode()
            sent = 0
            sock.settimeout(self.driver.wrtmout)
            while sent < len(reqRawData):
                sent += sock.send(reqRawData[sent:])

            #recv
            sock.settimeout(self.driver.rdtmout)
            headSize = self.driver.decoder.headDecoder.getHeadSize()
            recvRawHead = sock.recv(headSize)

            retryNum = 5
            while len(recvRawHead) < headSize and retryNum > 0:
                recvRawHead = recvRawHead + sock.recv(headSize - len(recvRawHead))
                retryNum -= retryNum

            if len(recvRawHead) < headSize:
                dlog.warning("driver get head failed")
                sock.close()
                self.__put_socket(None)
                return

            if hasattr(self.driver.decoder.headDecoder,"getBodySize"):
                bodySize = self.driver.decoder.headDecoder.getBodySize(recvRawHead)
                if bodySize != 0:
                    recvRawBody = sock.recv(bodySize)
                    while len(recvRawBody) < bodySize:
                        recvRawBody = recvRawBody + sock.recv(bodySize - len(recvRawBody))
                    self.driver.doDecode(recvRawHead + recvRawBody)
                else:
                    self.driver.doDecode(recvRawHead)
            else:
                self.driver.doDecode(recvRawHead)

            self.__put_socket(sock)

        except socket.error, why:
            dlog.warning("socket error (%s)", why)
            sock.close()
            self.__put_socket(None)
