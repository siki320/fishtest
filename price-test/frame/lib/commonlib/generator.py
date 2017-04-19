# -*- coding: GB18030 -*-
'''
Created on Aug 10, 2011

@author: caiyifeng<caiyifeng>

@summary: ����������
'''

import sys
import os
import traceback


class Generator(object):
    pass


class IdGen(Generator):
    def __init__(self):
        self.id = 1000      # ��һ���ù���ֵ
        
    def gen(self):
        if self.id >= sys.maxint:
            # ��һ���Ѿ���maxint�ˣ��׳��쳣
            raise StopIteration, "IdGen stops iteration"
        
        self.id += 1
        return self.id
    

class McidGen(Generator):
    '''
    @summary: Ϊ��������id��ȷ������id��mcid��Ψһ
    '''
    def __init__(self):
        self.mcid = 1500000000  # ��һ���ù���ֵ
        
    def gen(self):
        if self.mcid >= sys.maxint:
            # ��һ���Ѿ���maxint�ˣ��׳��쳣
            raise StopIteration, "McidGen stops iteration"
        
        self.mcid += 1
        return self.mcid


# QueryGen�е�query�б�
_query_list = []

def _init_query_list():
    # ��query_list.txt�ж�ȡquery�б�
    global _query_list
    
    # �õ�query_list.txt�ľ���·��
    # ͨ����ǰ�ļ�·����query_list.txt����ڵ�ǰ�ļ���·��������õ� 
    filepath = os.path.join(os.path.dirname(__file__), "../thirdlib/query_list.txt")

    # ��ȡ�ļ���ÿһ�У�����queryList
    queryListFile = open(filepath, 'r')
    for aquery in queryListFile:
        aquery = aquery.rstrip()
        if aquery:
            _query_list.append(aquery)
    queryListFile.close()
    
# ִ��query�б�ĳ�ʼ��
_init_query_list()

class QueryGen(Generator):
    def __init__(self):
        global _query_list
        self.it = iter(_query_list)     # ��ʼ���б������
        
    def gen(self):
        try:
            return self.it.next()
        except StopIteration, e:
            e.args = ["QueryGen stops iteration"]
            raise
        
    
class IpGen(Generator):
    '''
    @note: ip��ΧΪ[1.1.1.10] ~ [254.254.254.254]
    @note: ÿһλ��Ҫ�ܿ�0��255����ֹ����ĳЩ�����߼�
    '''
    def __init__(self):
        self.ip = [1, 1, 1, 9]     # ��һ���ù���ip
        
    def _ipinc(self, bit):
        '''
        @note: ��bitλ����1��bitλ�����λ��������Ϊ254
        @raise StopIteration: �������ʱ�׳�
        '''
        for i in range(bit - 1, -1, -1):
            # �ӵ�ǰλ��ʼ����
            if self.ip[i] < 254:
                # ��ǰλС��254�����Ӻ�����ѭ��
                self.ip[i] += 1
                break
            else:
                # ��ǰλ�Ѿ�Ϊ254�ˣ�������Ϊ1������������ǰһλ
                self.ip[i] = 1
        else:
            # ѭ��Խ�磬��ʾ�޷���������
            raise StopIteration, "IpGen stops iteration"
        
        # ��bit�����λ��������Ϊ254
        for i in range(bit, 4):
            self.ip[i] = 254
    
    def gen(self, bit=4):
        '''
        @note: ���ض�ռ��ip/ipƬ�Ρ�bit��ʾ�ڵڼ�λ�϶�ռ��ȡֵΪ1-4
        @note: ������˵������gen(3)������һ��3λ��ipƬ�� 'a.b.c'����ʾ��ռ'a.b.c.*'
        '''
        if not 1 <= bit <=4:
            raise Exception, "bit should be 1~4 in IpGen.gen()"
        
        self._ipinc(bit)
        return ".".join([str(i) for i in self.ip[0:bit]])


class CookieGen(Generator):
    '''
    @note: Cookie����ʽΪ32���ַ���ÿ���ַ���16�������֣�Ӣ����ĸ��д
    @note: ���صķ�ΧΪ '1'+'0'*30+'1' ~ 'F'*32
    '''
    def __init__(self):
        self.cookie = '1' + '0' * 31    # �ϴε�ʹ��ֵ
        
    def _cookieinc(self):
        cl = long(self.cookie, 16)
        cl += 1
        self.cookie = "%X" % cl
        
    def gen(self):
        if self.cookie == 'F' * 32:
            # ��һ���Ѿ��õ����ֵ��
            raise StopIteration, "CookieGen stops iteration"
        
        self._cookieinc()
        return self.cookie


class UrlStruct(object):
    '''@summary: url�ṹ������url, site, domain��������'''
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
        self.index = 1000   # ��һ���ù���ֵ
        
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

