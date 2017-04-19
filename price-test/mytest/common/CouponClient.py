# encoding: utf-8

import time
import os
import sys
import urllib
import urllib2

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../lib/test_common/gen-py')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../lib/test_common/thrift')))
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from dups_price_coupon import DupsPriceCoupon
from dups_price import ttypes as coupon_ttypes
from config.config import EnvGlobal
# from mytest.common.lib_import import *
from frame.lib.commonlib.dlog import dlog


class COUPON_CLIENT():

    def __init__(self, ip_thrift=EnvGlobal.Coupons_Ip, port_thrift=EnvGlobal.Coupons_Port):
        self.ip_thrift = ip_thrift
        self.port_thrift = port_thrift

        self.protocol = None
        self.client = None
        self.transport = None


    def check_thrift(self, package=""):
        try:
            if self.transport is None:
                self.transport = TSocket.TSocket(self.ip_thrift, self.port_thrift)
                # ("IP: %r, Port: %r" %(self.ip, self.port))
                self.transport = TTransport.TFramedTransport(self.transport)
                self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
                self.client = PriceService.Client(self.protocol)
                self.transport.open()
        except Exception, ex:
            print ex
            return False
        return True

    def close(self):
        try:
            if not self.transport is None:
                self.transport.close()
                self.transport = None
        except Exception as ex:
            print ex
            return False
        return True


    def CouponRes(self, **kwargs):

        coupon_tb = coupon_ttypes.DupsPriceRequest()


        for key in kwargs:
            setattr(coupon_tb, key, kwargs[key])


        self.check_thrift()
        dlog.info(
            "===============================Thrift PriceRes: dp: %r ==============================" % (
             coupon_tb))
        self.print_ip_port(self.ip_thrift, self.port_thrift)

        res = self.client.computeDiscount(coupon_tb)
        self.close()
        return res


    def CouponReal(self, pid=None):

        coupon_tb = coupon_ttypes.DupsPriceRequest()

        serviceName = "matis";
        productId = 3;
        subsidyChannel = 3;
        phonr = "13100000000"
        
        setattr(coupon_tb, "serviceName", serviceName)
        setattr(coupon_tb, "productId", productId)
        setattr(coupon_tb, "subsidyChannel", subsidyChannel)
        setattr(coupon_tb, "pid", pid)
        setattr(coupon_tb, "phone", phone)

        self.check_thrift()
        dlog.info(
            "===============================Thrift PriceRes: dp: %r ==============================" % (
             coupon_tb))
        self.print_ip_port(self.ip_thrift, self.port_thrift)

        res = self.client.computeDiscount(coupon_tb)
        self.close()
        return res

    def print_ip_port(self, ip, port):
        dlog.info("[DP Trift/HTTP] IP: %r, Port: %r" % (ip, port))

def test_price_res(client):
    print client.computeDiscount()

if __name__ == '__main__':

    client = Coupon_CLIENT("127.0.0.1", 9001)
    print test_price_res(client)




