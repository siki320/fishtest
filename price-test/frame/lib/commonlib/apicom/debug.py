# -*- coding: gb2312 -*- 

import share;

ALL_TEST_MODE = ['NORMAL','DEBUG','EXCEPTION'];

def getTestMode():  
    try:
        return share.debug;
    except:
        return 'DEBUG';

def setTestMode(mode):
    try:
        share.debug = mode;
    except:
        share.debug = 'DEBUG';
    
