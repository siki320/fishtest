# encoding: utf-8
'''
@author:
@date:
'''
# from mytest.lib.test_common.locsvr_thrift_client import LOCSVR_THRIFT_CLIENT
# from mytest.lib.util import *

# from mytest.lib.test_common.thrift import *
from mytest.common.lib_import import *
from config.case_config import *

class BaseCase(MyCase):
    def __init__(self):
        """
        """
        super(BaseCase, self).__init__()

    price_client = PRICE_CLIENT()
    coupon_client = COUPON_CLIENT()
    
    def base_test(self,stg,key):
        
        res1 = self.price_client.PriceResReal(key[1],key[2],key[3],key[4],key[5],key[6],key[7],key[8],key[9],key[10],key[11])
        print "price response: %r "  % res1
 #       res2 = self.coupon_client.CouponReal(key[7])
 #       print "coupon response: %r " % res2
        self.check_res(res1, stg, key[12],key[13])

    def test_stg(self):
        count = 0
        for key in CaseConfig.run_case:
            count += 1
            print "\n"
            dlog.info("*"*10 + "Test Case: Test passenger_id=[%s]" + "*"*10, key[7])
            print "\n"

            self.base_test(key[0],key)


    #======================================================
    def check_res(self, priceres, stg, expecterrno,expectdis):
            # print require_level
	assert_equal(priceres.err_no, expecterrno, "Test stg=%s, err_no is wrong, exp: err_no=0, act: err_no=%d" % (stg, priceres.err_no))








