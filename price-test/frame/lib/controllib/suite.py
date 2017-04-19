# -*- coding: GB18030 -*-
'''
Created on Nov 9, 2011

@author: caiyifeng<caiyifeng>

@summary: ����ִ��case�Ļ���
'''

class DtestSuite(object):
    def __init__(self):
        self.caselist = []          # case�����б�, �ö��������DtestCase�����ʵ��
        self.testdict = {}          # <case, testlist>���ֵ�
        
    def addcase(self, acase):
        self.caselist.append(acase)
    
    def add_test_dict(self, acase, tests):
        self.testdict[acase] = tests

    def run_suite(self, result):
        '''@summary: �������е�case
        @param result: DResult����'''
        pass
    
    def get_testlist(self):
        '''@summary: ����test list'''
        testlist = []
        for acase in self.testdict.keys():
            for atest in self.testdict[acase]:
                testlist.append(acase.get_relpath()+":"+atest.__name__)
        return testlist
    def clear(self):
        '''@summary: ����case��test'''
        self.caselist = []
        self.testdict = {}
