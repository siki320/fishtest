# -*- coding: GB18030 -*-
'''
Created on Nov 9, 2011

@author: caiyifeng<caiyifeng>

@summary: 调度执行case的基类
'''

class DtestSuite(object):
    def __init__(self):
        self.caselist = []          # case对象列表, 该对象必须是DtestCase子类的实例
        self.testdict = {}          # <case, testlist>的字典
        
    def addcase(self, acase):
        self.caselist.append(acase)
    
    def add_test_dict(self, acase, tests):
        self.testdict[acase] = tests

    def run_suite(self, result):
        '''@summary: 运行所有的case
        @param result: DResult对象'''
        pass
    
    def get_testlist(self):
        '''@summary: 生成test list'''
        testlist = []
        for acase in self.testdict.keys():
            for atest in self.testdict[acase]:
                testlist.append(acase.get_relpath()+":"+atest.__name__)
        return testlist
    def clear(self):
        '''@summary: 汕蹇誧ase和test'''
        self.caselist = []
        self.testdict = {}
