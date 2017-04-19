# -*- coding: GB18030 -*-
'''
Created on Aug 10, 2011

@author: caiyifeng<caiyifeng>

@summary: 数据生成器
'''

import sys
import os
import traceback


class Generator(object):
    pass


class IdGen(Generator):
    def __init__(self):
        self.id = 1000      # 上一次用过的值
        
    def gen(self):
        if self.id >= sys.maxint:
            # 上一次已经是maxint了，抛出异常
            raise StopIteration, "IdGen stops iteration"
        
        self.id += 1
        return self.id
    

class McidGen(Generator):
    '''
    @summary: 为物料生成id，确保物料id（mcid）唯一
    '''
    def __init__(self):
        self.mcid = 1500000000  # 上一次用过的值
        
    def gen(self):
        if self.mcid >= sys.maxint:
            # 上一次已经是maxint了，抛出异常
            raise StopIteration, "McidGen stops iteration"
        
        self.mcid += 1
        return self.mcid


# QueryGen中的query列表
_query_list = []

def _init_query_list():
    # 从query_list.txt中读取query列表
    global _query_list
    
    # 得到query_list.txt的绝对路径
    # 通过当前文件路径、query_list.txt相对于当前文件的路径，计算得到 
    filepath = os.path.join(os.path.dirname(__file__), "../thirdlib/query_list.txt")

    # 读取文件的每一行，加入queryList
    queryListFile = open(filepath, 'r')
    for aquery in queryListFile:
        aquery = aquery.rstrip()
        if aquery:
            _query_list.append(aquery)
    queryListFile.close()
    
# 执行query列表的初始化
_init_query_list()

class QueryGen(Generator):
    def __init__(self):
        global _query_list
        self.it = iter(_query_list)     # 初始化列表迭代器
        
    def gen(self):
        try:
            return self.it.next()
        except StopIteration, e:
            e.args = ["QueryGen stops iteration"]
            raise
        
    
class IpGen(Generator):
    '''
    @note: ip范围为[1.1.1.10] ~ [254.254.254.254]
    @note: 每一位需要避开0和255，防止触发某些特殊逻辑
    '''
    def __init__(self):
        self.ip = [1, 1, 1, 9]     # 上一次用过的ip
        
    def _ipinc(self, bit):
        '''
        @note: 在bit位上增1。bit位后面的位，都设置为254
        @raise StopIteration: 增加溢出时抛出
        '''
        for i in range(bit - 1, -1, -1):
            # 从当前位开始遍历
            if self.ip[i] < 254:
                # 当前位小于254，增加后跳出循环
                self.ip[i] += 1
                break
            else:
                # 当前位已经为254了，则重置为1，并继续增加前一位
                self.ip[i] = 1
        else:
            # 循环越界，表示无法继续增加
            raise StopIteration, "IpGen stops iteration"
        
        # 把bit后面的位，都设置为254
        for i in range(bit, 4):
            self.ip[i] = 254
    
    def gen(self, bit=4):
        '''
        @note: 返回独占的ip/ip片段。bit表示在第几位上独占，取值为1-4
        @note: 举例来说，调用gen(3)，返回一个3位的ip片段 'a.b.c'，表示独占'a.b.c.*'
        '''
        if not 1 <= bit <=4:
            raise Exception, "bit should be 1~4 in IpGen.gen()"
        
        self._ipinc(bit)
        return ".".join([str(i) for i in self.ip[0:bit]])


class CookieGen(Generator):
    '''
    @note: Cookie的形式为32个字符，每个字符是16进制数字，英文字母大写
    @note: 返回的范围为 '1'+'0'*30+'1' ~ 'F'*32
    '''
    def __init__(self):
        self.cookie = '1' + '0' * 31    # 上次的使用值
        
    def _cookieinc(self):
        cl = long(self.cookie, 16)
        cl += 1
        self.cookie = "%X" % cl
        
    def gen(self):
        if self.cookie == 'F' * 32:
            # 上一次已经用到最大值了
            raise StopIteration, "CookieGen stops iteration"
        
        self._cookieinc()
        return self.cookie


class UrlStruct(object):
    '''@summary: url结构，包含url, site, domain三个属性'''
    def __init__(self, domain):
        self.domain = domain
        
    def _getsite(self):
        return "www." + self.domain
    
    site = property(_getsite)

    def _geturl(self):
        return "http://" + self.site + "/dtsurl.html"
    
    url = property(_geturl)
    
    def __str__(self):
        return self.url

class UrlGen(Generator):
    def __init__(self):
        self.index = 1000   # 上一次用过的值
        
    def gen(self):        
        if self.index >= sys.maxint:
            raise StopIteration, 'UrlGen Stops Iteration'
        
        self.index += 1
        return UrlStruct("dts-%s.com" % self.index)


def _test_idgen():
    print "idgen"
    idgen = IdGen()
    print idgen.gen()
    print idgen.gen()
    try:
        idgen.id = sys.maxint - 10
        while True:
            ret = idgen.gen()
    except StopIteration:
        print ret
        traceback.print_exc()
        print
    
def _test_mcidgen():
    print "mcidgen"
    mcidgen = McidGen()
    print mcidgen.gen()
    print mcidgen.gen()
    try:
        mcidgen.mcid = sys.maxint - 10
        while True:
            ret = mcidgen.gen()
    except StopIteration:
        print ret
        traceback.print_exc()
        print
    
def _test_querygen():
    print "querygen"
    querygen = QueryGen()
    print querygen.gen()
    print querygen.gen()
    try:
        while True:
            ret = querygen.gen()
    except StopIteration:
        print ret
        traceback.print_exc()
        print
    
def _test_ipgen():
    print "ipgen"
    ipgen = IpGen()
    print ipgen.gen(bit=1)
    print ipgen.gen(bit=2)
    print ipgen.gen(bit=3)
    print ipgen.gen(bit=4)
    try:
        ipgen.ip = [254, 254, 254, 244]
        while True:
            ret = ipgen.gen()
    except StopIteration:
        print ret
        traceback.print_exc()
        print
    
def _test_cookiegen():
    print "cookiegen"
    cookiegen = CookieGen()
    print cookiegen.gen()
    print cookiegen.gen()
    try:
        cookiegen.cookie = "F" * 31 + "0"
        while True:
            ret = cookiegen.gen()
    except StopIteration:
        print ret
        traceback.print_exc()
        print
    
def _test_urlgen():
    print "urlgen"
    urlgen = UrlGen()
    print urlgen.gen()
    print urlgen.gen()
    try:
        urlgen.index = sys.maxint - 10
        while True:
            ret = urlgen.gen()
    except StopIteration:
        print ret
        traceback.print_exc()
        print
    
if __name__ == "__main__":
    _test_idgen()
    _test_mcidgen()
    _test_querygen()
    _test_ipgen()
    _test_cookiegen()
    _test_urlgen()

