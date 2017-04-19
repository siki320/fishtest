# -*- coding: GB18030 -*-
'''
Created on Feb 22, 2011

@author: caiyifeng

@summary: ��ʱ��
'''

import time

class Timer(object):
    '''
    @summary: �ֽ׶λ��ܼ�ʱ����
    @note: ʹ�÷����� (start -> ... -> end) -> ... -> (start -> ... -> end)
    @note: totaltime��¼����start/end��֮���ʱ���ܺ�
    '''

    def __init__(self):
        self.totaltime = 0.0      # ����ʱ������������λ��
        self._starttime = 0.0     # ��һ�ο�ʼ��ʱ��ʱ�䣬����������λ��
        
    def start(self):
        '''@summary: ��ʼ��ʱ'''
        self._starttime = time.time()
    
    def end(self):
        '''
        @summary: ������ʱ������������ʱ
        '''
        endtime = time.time()
        self.interval = endtime - self._starttime
        self.totaltime += self.interval

    def __add__(self, y):
        self.totaltime += y.totaltime
        return self
    
    
class Timer2(object):
    '''
    @summary: ���׶μ�ʱ����
    @note: ʹ�÷����� (init)start -> ... -> end -> ... -> end
    @note: ����start�����һ��end֮���ʱ��
    '''
    
    def __init__(self):
        self._starttime = 0.0       # start��ʼ��ʱ��ʱ�䣬����������λ��
        self._interval = 0.0 
        
        self.start()    # Ĭ�ϳ�ʼ��ʱ���Ϳ�ʼ��ʱ
        
    def start(self):
        '''@summary: ��ʼ��ʱ'''
        self._starttime = time.time()
        
    def end(self):
        '''
        @summary: ������ʱ
        @return: ��start��ʱ����
        '''
        endtime = time.time()
        self._interval = endtime - self._starttime
        return self._interval

    def get_sec(self):
        "ת������"
        return self._interval

    def get_min(self):
        "ת�ɷ���"
        return self._interval/60    
    
def _test_timer():
    print "_test_timer"
    t = Timer()
    
    t.start()
    time.sleep(1)
    t.end()
    print t.totaltime   # expect 1
    
    time.sleep(2)   # ���ᱻ��������
    
    t.start()
    time.sleep(3)
    t.end()
    print t.totaltime   # expect 1+3 = 4

def _test_timer2():
    print "_test_timer2"
    t = Timer2()
    
    time.sleep(1)
    print t.end()   # expect 1
    
    time.sleep(2)   # �ᱻ��������
    
    time.sleep(3)   # expect 1+2+3 = 6
    print t.end()

if __name__ == "__main__":
    _test_timer()
    print
    _test_timer2()

