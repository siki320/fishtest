# encoding: utf-8

import time
import os
import sys
import urllib
import urllib2

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../lib/test_common/gen-py')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../lib/test_common/')))
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from dups_price import PriceService
from dups_price import ttypes as dp_ttypes
from config.config import EnvGlobal
# from mytest.common.lib_import import *
from frame.lib.commonlib.dlog import dlog


class PRICE_CLIENT():

    def __init__(self, ip_thrift=EnvGlobal.DP_Thrift_IP, port_thrift=EnvGlobal.DP_Thrift_Port,
                 ip_http=EnvGlobal.DP_Http_IP, port_http=EnvGlobal.Dp_Http_Port):
        self.ip_http = ip_http
        self.port_http = port_http

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


    def PriceRes(self, **kwargs):

        dp_tb = dp_ttypes.PriceReq()


        for key in kwargs:
            setattr(dp_tb, key, kwargs[key])


        self.check_thrift()
        dlog.info(
            "===============================Thrift PriceRes: dp: %r ==============================" % (
             dp_tb))
        self.print_ip_port(self.ip_thrift, self.port_thrift)

        res = self.client.price(dp_tb)
        self.close()
        return res


    def PriceResReal(self, product_id=None, area=None,flat=None,
                 flng=None,tlat=None,tlng=None,passengerid=None,road_distance=None,eta=None,pre_total_fee=None,bubble_id=None):

        dp_trace = dp_ttypes.Trace(traceId="0x1234beef",spanId="10000",caller="dups-api")
        dp_tb = dp_ttypes.PriceReq()
        ctime = 1480562059
        passenger_phone = "13100000000"
        app_version = "5.0.12"
        stg_name = "sid"
        req_type = 3
	user_type = 1

        setattr(dp_tb, "product_id", product_id)
        setattr(dp_tb, "area", area)
        setattr(dp_tb, "flat", flat)
        setattr(dp_tb, "flng", flng)
        setattr(dp_tb, "tlat", tlat)
        setattr(dp_tb, "tlng", tlng)
        setattr(dp_tb, "passengerid", passengerid)
        setattr(dp_tb, "passenger_phone", passenger_phone)
        setattr(dp_tb, "user_type",user_type)
	setattr(dp_tb, "road_distance", road_distance)
        setattr(dp_tb, "eta", eta)
        setattr(dp_tb, "pre_total_fee", pre_total_fee)
        setattr(dp_tb, "stg_name", stg_name)
        setattr(dp_tb, "req_type", req_type)
        setattr(dp_tb, "trace", dp_trace)
        setattr(dp_tb, "ctime", ctime)
        setattr(dp_tb, "bubble_id", bubble_id)
        setattr(dp_tb, "app_version", app_version)
#       setattr(dp_tb, "app_channel", app_channel)


        self.check_thrift()
        dlog.info(
            "===============================Thrift PriceRes: dp: %r ==============================" % (
             dp_tb))
        self.print_ip_port(self.ip_thrift, self.port_thrift)

        res = self.client.price(dp_tb)
        self.close()
        return res
        
    def Http_price(self, path="/shield-arch/price", urlparm=None):
        ip = self.ip_http
        port = self.port_http

        urlparm['traceid']= int(time.time())

        url_values = urllib.urlencode(urlparm)
        url = 'http://%s:%s%s' % (ip, str(port), path)
        full_url = url + '?' + url_values
        dlog.info( "url: %s" % full_url)

        try:
            resp = urllib2.urlopen(full_url)
        except:
            print "error: exception!"
            return None

        rsp_data = resp.read()
        # print "response:", rsp_data

        return rsp_data
        # print data

    def print_ip_port(self, ip, port):
        dlog.info("[DP Trift/HTTP] IP: %r, Port: %r" % (ip, port))

def test_price_res(client):
    print client.PriceRes()

def test_price_http(client):
    urldata = {"passenger_id":123}
    print client.Http_price(urlparm=urldata)

if __name__ == '__main__':

    # client = DP_THRIFT_CLIENT("127.0.0.1", 9901)
    # client = DP_CLIENT("127.0.0.1", 9900)
    client = PRICE_CLIENT("127.0.0.1", 9000)

    # test_price_res(client)
    test_price_http(client)




