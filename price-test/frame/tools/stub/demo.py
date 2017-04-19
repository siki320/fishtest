# -*- coding: GB18030 -*-
'''
'''

import os
os.sys.path.append(os.path.dirname(os.path.abspath(__file__))+"/../../../")

from frame.lib.commonlib.dlog import dlog
from frame.tools.stub.BaseStub import BaseStub

#log
dlog.init_logger("./stub_demo.log")

#make driver
stub = BaseStub({"name":"test","port":1112})

#call back func
def mycallbackfunc(stub):
    stub.res['body'] = {"name":"stub demo"}

#set body
stub.setCallback(mycallbackfunc)

#start the stub
stub.start()

#loop&stop
try:
    while 1:
        import time
        time.sleep(0.5)
except KeyboardInterrupt:
    print("Crtl+C pressed. Shutting down.")
    stub.stop()
