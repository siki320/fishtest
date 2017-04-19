# -*- coding: GB18030 -*-
'''
Created on Feb 22, 2011

@author: caiyifeng

@summary: 计时器
'''

import time

class Timer(object):
    '''
    @summary: 分阶段汇总计时器类
    @note: 使用方法： (start -> ... -> end) -> ... -> (start -> ... -> end)
    @note: totaltime记录所有start/end对之间的时间总和
    '''

    def __init__(self):
        self.totaltime = 0.0      # 总用时，浮点数，单位秒
        self._starttime = 0.0     # 上一次开始计时的时间，浮点数，单位秒
        
    def start(self):
        '''@summary: 开始计时'''
        self._starttime = time.time()
    
    def end(self):
        '''
        @summary: 结束计时，并增加总用时
        '''
        endtime = time.time()
        self.interval = endtime - self._starttime
        self.totaltime += self.interval

    def __add__(self, y):
        self.totaltime += y.totaltime
        return self
    
    
class Timer2(object):
    '''
    @summary: 单阶段计时器类
    @note: 使用方法： (init)start -> ... -> end -> ... -> end
    @note: 返回start到最后一个end之间的时间
    '''
    
    def __init__(self):
        self._starttime = 0.0       # start开始计时的时间，浮点数，单位秒
        self._interval = 0.0 
        
        self.start()    # 默认初始化时，就开始计时
        
    def start(self):
        '''@summary: 开始计时'''
        self._starttime = time.time()
        
    def end(self):
        '''
        @summary: 结束计时
        @return: 到start的时间间隔
        '''
        endtime = time.time()
        self._interval = endtime - self._starttime
        return self._interval

    def get_sec(self):
        "转换成秒"
        return self._interval

    def get_min(self):
        "转成分钟"
        return self._interval/60    
    
def _test_timer():
    print "_test_timer"
    t = Timer()
    
    t.start()
    time.sleep(1)
    t.end()
    print t.totaltime   # expect 1
    
    time.sleep(2)   # 不会被计算在内
    
    t.start()
    time.sleep(3)
    t.end()
    print t.totaltime   # expect 1+3 = 4

def _test_timer2():
    print "_test_timer2"
    t = Timer2()
    
    time.sleep(1)
    print t.end()   # expect 1
    
    time.sleep(2)   # 会被计算在内
    
    time.sleep(3)   # expect 1+2+3 = 6
    print t.end()

if __name__ == "__main__":
    _test_timer()
    print
    _test_timer2()

