# encoding: utf-8
from mytest.common.lib_import import *

class CaseConfig(object):
    #配置运行的case, run_case 参数:
    #参数0-11：case名称,product_id,area,flat,flng,tlat,tlng,passengerid,road_distance,eta,pre_total_fee,bubble_id
    #参数12-13:期望errno，期望discount
    run_case = [
        ["formal", 3, 6, 32.087982,118.800575,32.05034,118.7794,7447607,10803,40,40,"dpkey_a6e466d2309560f0219f433a9cd54793_3_5_0_13588311326_116001790_20172301912347",0,0.4],

    ]

