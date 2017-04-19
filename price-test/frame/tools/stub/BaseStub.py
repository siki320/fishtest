# -*- coding:utf-8 -*-
"""
"""

import time
import socket,threading,asyncore
from frame.lib.commonlib.dlog import dlog
from frame.tools.lib.core import InterfaceMetaData

class BaseStub(object):

    def __init__(self, cfg):
        self.port = int(cfg.get("port",23456))
        self.name = cfg.get("name","base_stub")
        #self.verbose = cfg.get("verbose",1)
        self.rdtmout = cfg.get("readtimeout",0.2)
        self.wrtmout = cfg.get("writetimeout",0.2)
        self.conntype = cfg.get("conntype",0)
        self.threadnum = cfg.get("threadnum",1)
        self.queuesize = cfg.get("queuesize",2)

        self.net = StubNetLib(self)
        self.req = InterfaceMetaData()
        self.res = InterfaceMetaData()
        self.raw_req = None
        self.raw_res = None
        self.callback = None

    def decode(self,data):
        self.raw_req = data
        self.req.clear()
        self.req["head"],self.req["body"] = self.decoder.decode(data)

    def encode(self):
        if self.raw_res != None:
            return self.raw_res

        if self.res.body_set_flag == False:
            raise RuntimeError,'request body must set'
        elif self.res.head_set_flag == False:
            self.res["head"] = self.encoder.headEncoder.getDefaultHead()

        return self.encoder.encode(self.res["head"],self.res["body"])

    def doDecode(self,data):
        self.decode(data)

        prefix = "\n" + "\033[4;31m" + "+"*10 + " [IN STUB] : " + self.name.upper() + " [REQUEST] " + "+"*10 + "\033[0m"
        logstr = prefix + str(self.req)
        dlog.debug(logstr)

    def doEncode(self):
        rawData = self.encode()

        prefix = "\n" + "\033[4;31m" + "+"*10 + " [IN STUB] : " + self.name.upper() + " [RESPONSE] " + "+"*10 + "\033[0m"
        logstr = prefix + str(self.res)
        dlog.debug(logstr)

        return rawData

    def setCallback(self, cb):
        self.callback = cb

    def start(self):
        self.bt = threading.Thread(target = self.net.start)
        self.bt.start()
        #wait for thread start
        time.sleep(0.001)

    def stop(self):
        self.net.stop()
        #wait for port reuse
        time.sleep(0.01)
        #self.bt.join()

    def clear(self):
        self.req.clear()
        self.res.clear()
        self.raw_req = None
        self.raw_res = None
        self.callback = None


class StubNetLib(asyncore.dispatcher):

    def __init__(self,stub):
        asyncore.dispatcher.__init__(self)
        self.stub = stub
        self.is_running = False
        self.conncond = threading.Condition()
        self.twork = []
        self.connections = []
        self.__lock = threading.Lock()

    def start(self):
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(("", self.stub.port))
        self.listen(self.stub.queuesize)
        self.twork = []
        self.connections = []

        self.is_running = True
        for i in range(self.stub.threadnum):
            self.twork.append(threading.Thread(target = self.thread_work))
        for i in range(self.stub.threadnum):
            self.twork[i].start()

        asyncore.loop(0.01)

    def stop(self):
        if self.is_running == True:
            self.is_running = False
            for i in range(self.stub.threadnum):
                self.twork[i].join()
            self.del_channel()
            self.close()

    def thread_work(self):
        while self.is_running:
            conn = self.__get_conn()
            if not conn: break

            try:
                self.__lock.acquire()
                sock,addr = conn

                #recv
                sock.settimeout(self.stub.rdtmout)

                headSize = self.stub.decoder.headDecoder.getHeadSize()
                recvRawHead = sock.recv(headSize)

                retryNum = 5
                while len(recvRawHead) < headSize and retryNum > 0:
                    recvRawHead = recvRawHead + sock.recv(headSize - len(recvRawHead))
                    retryNum -= retryNum

                if len(recvRawHead) < headSize:
                    dlog.warning("stub get head failed")
                    conn[0].close()
                    self.__lock.release()
                    continue

                if hasattr(self.stub.decoder.headDecoder,"getBodySize"):
                    bodySize = self.stub.decoder.headDecoder.getBodySize(recvRawHead)
                    if bodySize != 0:
                        recvRawBody = sock.recv(bodySize)
                        while len(recvRawBody) < bodySize:
                            recvRawBody = recvRawBody + sock.recv(bodySize - len(recvRawBody))
                        self.stub.doDecode(recvRawHead + recvRawBody)
                    else:
                        self.stub.doDecode(recvRawHead)
                else:
                    self.stub.doDecode(recvRawHead)

                #callback
                if self.stub.callback:
                    self.stub.callback(self.stub)
                else:
                    self.__lock.release()
                    raise RuntimeError,'callbackfunc must set first'

                #send
                sock.settimeout(self.stub.wrtmout)
                sendRawData = self.stub.doEncode()
                sent = 0
                while sent < len(sendRawData):
                    sent += sock.send(sendRawData[sent:])

                if self.stub.conntype:
                    self.__put_conn(conn)
                else:
                    conn[0].close()
                self.__lock.release()
            except socket.error, why:
                self.__lock.release()
                dlog.warning("socket[%d] %s", conn[0].fileno(), why)
                conn[0].close()
                

    def handle_accept(self):
        try:
            conn = self.accept()
        except socket.error:
            dlog.warning("stub accept() threw an exception")
            return
        except TypeError:
            dlog.warning("stub accept() threw EWOULDBLOCK")
            return
        if conn: self.__put_conn(conn)

    def __get_conn(self):
        self.conncond.acquire()
        while len(self.connections) == 0 and self.is_running:
            self.conncond.wait(1)
        if not self.is_running:
            self.conncond.release()
            return None
        conn = self.connections.pop(0)
        self.conncond.release()
        return conn

    def __put_conn(self, conn):
        self.conncond.acquire()
        self.connections.append(conn)
        self.conncond.notify()
        self.conncond.release()
