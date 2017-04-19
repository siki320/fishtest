# -*- coding: GB18030 -*-
# '''
# Created on Dec 11, 2011
# @author: maqi<maqi>
# @summary: dts driver demo
# '''

import os
os.sys.path.append(os.path.dirname(os.path.abspath(__file__))+"/../../../")

from frame.lib.commonlib.dlog import dlog
from frame.tools.driver.NsheadMcpackDriver import NsheadMcpack2Driver

#log
dlog.init_logger("./driver_demo.log")

#make driver
driver = BaseDriver({"name":"test","port":"1112"})

#send data dict
pack_dict = {'head': {'user_ip': 4192211372, 'cookie': 'D3E9A417BC388520534E6FC85EB8D39B', 'log_id1': 599136522, 'src_num': 1, 'log_id2':
194839849}, 'src_req': [{'src_id': 14L, 'req_num': 0}]}

#set body
driver.setRequestBody(pack_dict)

#do request
driver.doRequest()
