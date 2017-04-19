# -*- coding: GB18030 -*-
'''

����ʹ��configure

Created on Jan 16, 2012

@author: tanyi<tanyi>
��yifengǨ��

��ģ��ʵ�ֵ��Ƕ�һЩconf�ļ��ľ��Զ�λ��ʽ���޸ķ�����
�������ݱȽ϶��ģ������ܹ����Զ�λ���о�ȷ�޸�
�޸�ʱ���ݵĲ������£�
@keypath �� name:pos#name:pos#name:pos
            name��ָ�ļ��еĽڵ㣬pos��ָ���ҵ����ڵ���
            ��pos���ڵ㣬posֵ�ǿ��Բ����õģ�������Ĭ��
            �޸ĵ�һ��,pos��ֵ��1��ʼ!
@key���޸ĵ�keyֵ
@value���¼ӵ�valueֵ
���keypathΪ�գ���ô���޸�ȫ�ֵ�kvֵ
ʾ����
�����ļ�
[mola]
[.@metaserver]
ip : 10.65.45.30
query_port : 7000
update_port : 7001

[.@metaserver]
ip : 10.65.45.31
query_port : 7000
update_port : 7001

[.@metaserver]
ip : 10.65.45.32
query_port : 7000
update_port : 7001
���Ҫ�޸�ip : 10.65.45.32�Ĵ���ֵ,��ip�޸�Ϊ127.0.0.1�����ݲ������£�
 uc.set_value('[mola]#[.@metaserver]:3', 'ip', '127.0.0.1')
'''

import os
import string


class Ubconf(object):
    '''
     ��ʼ���ö����ʱ�� is_add�ֶα�ʾ���޸�key������ʱ���Ƿ�������Ӧ��key
    '''
    def __init__(self, _is_add = 0):
        self.global_dict = {}
        self.is_add = _is_add
        self.root_list = []
        for i in range(0, 5):
            self.root_list.append([])
        self.lines = []

    def get_fromfile(self, path = 'bs_info.conf'):
        if os.path.exists(path):
            f = open(path, 'r')
            fstr = f.read()
            #self.lines = fstr.splitlines()
            self.set_str(fstr)
            f.close()
        else:
            print 'file open error'
            self.lines = []
        #self.do_ub_conf()

    def set_str(self, _str):
        '''��conf�ļ�����str����ʽ��ֵ ���÷�ʽ����ֱ��Ϊset_str(f.read())'''
        self.global_dict = {}
        self.root_list = []
        for i in range(0, 5):
            self.root_list.append([])
        self.lines = []
        self.lines = _str.splitlines()
        self.do_ub_conf()

    def f_line(self, line):
        line = line.replace('\t', '')
        line = line.replace(' ', '')
        return line

    def do_ub_conf(self):
        '''
        �����ļ�����������:
        k:v    --global kv
        []     --level 0
        [.]    --level 1
        [..]   --level 2
        [...]  --level 3
        [...]  --level 3
        [..]   --level 2
        [...]  --level 3
        [...]  --level 3
        [.]    --level 1
        [..]   --level 2
        [...]  --level 3
        [...]  --level 3
        [..]   --level 2
        [...]  --level 3
        [...]  --level 3
        '''
        root = self.root_list
        #root[num][]��ʾ level num�Ľڵ�list
        #�����ļ�������root[num][len(root[num])-1]�ĸ��ڵ�һ����root[num-1][len(root[num-1])-1]
        #һ��root[][]����������root[][][node_key, value_dict{}, chd_list[]]
        cur_list = []
        is_gb = 1#����Ƿ������ȫ��dict��ʽ�������k-v�������κ�[]��ʽ�Ľڵ�
        for line in self.lines:
            line = self.f_line(line)
            if len(line) <= 0 or line[0] == '#':
                continue
            #print line
            if line.find('[') == 0 and line.find(']') != -1:
                is_gb = 0
                num = line.count('.')
                #print num
                t_list = []
                t_list.append(line)
                value_dict = {}
                t_list.append(value_dict)
                chd_list = []
                t_list.append(chd_list)
                cur_list = t_list 
                root[num].append(t_list)
                #��һ�㼶�ڵ�ָ��
                if num >= 1 and (num-1) < len(root):
                    inx = len(root[num-1]) - 1
                    if inx >= 0 and inx < len(root[num-1]) and len(root[num-1][inx]) >= 2:
                        root[num-1][inx][2].append(t_list)
                    else:
                        print 'inx is out of range! inx = ', inx
                else:
                    pass
                    #print line
                #����һ�㼶���ӿսڵ㣬��ֹ���ϲ�
                next_list = []
                next_dict = {}
                next_chds = []
                next_list.append('#')
                next_list.append(next_dict)
                next_list.append(next_chds)
                root[num+1].append(next_list)
                t_list[2].append(next_list)
            else:
                if is_gb == 1:
                    self.line2dict(line, self.global_dict, ':')
                else:
                    cur_dict = cur_list[1]
                    self.line2dict(line, cur_dict, ':')
    
    def line2dict(self, line, _dict, seg):
        if line.find(seg) == -1:
            return 
        s = line.split(seg)
        if len(s) >= 2:
            _dict[s[0]] = s[1]
            for inx in range(2, len(s)):
                _dict[s[0]] += (seg+s[inx])
        else:
            print 'error line = ', line
     
    def dict2lines(self, _dict, _lines, seg):
        _keys = _dict.keys()
        for item in _keys:
            _lines.append(item+seg+_dict[item])

    def get_pos(self, _str):
        pos = -1
        if _str.find(':') != -1:
            s = _str.split(':')
            if len(s) >= 2 and s[1].isdigit():
                pos = string.atol(s[1])
                return pos
            else:
                print 'error _str = ', _str
        return -1

    def insert_value(self, _dict, _key, _value):
        #print _dict
        if _dict.has_key(_key) or self.is_add == 1:
            _dict[_key] = _value
            return True
        else:
            print 'key = ',_key,' is not exists!'
        return False
    
    def trace_value(self, child_list, _kpl, inx, _key, _value):
        #for i in range(0, inx):
        #    print '-',
        #print
        #�����νṹ�в��ҽڵ�����޸�
        if inx < 0 or inx >= len(_kpl) or inx > 5 or len(child_list) == 0:
            return False
        pos = self.get_pos(_kpl[inx])
        if pos == 0:
            print 'find a pos = 0, pos starts from 1'
            return False
        if pos != -1:
            if len(child_list) < pos:
                print 'find a index of ',  _kpl[inx], 'out of range!'
                return False
            cnt = 0
            name = _kpl[inx].split(':')
            for item in child_list:
                if item[0] == name[0]:
                    cnt += 1
                if cnt == pos:
                    #print item[0]
                    if inx == len(_kpl) -1:
                        return self.insert_value(item[1], _key, _value)
                    else:
                        return self.trace_value(item[2], _kpl, (inx+1), _key, _value)
            print 'find a index of ',  _kpl[inx], 'out of range!'
        else:
            for item in child_list:
                print item[0], _kpl[inx]
                if item[0] == _kpl[inx]:
                    if inx == len(_kpl) - 1:
                        return self.insert_value(item[1], _key, _value)
                    ret = self.trace_value(item[2], _kpl, (inx+1), _key, _value)
                    if ret == True:
                        return ret
            print 'can not find ', _kpl[inx]     
        return False
        

    def set_value(self, _key_path='', _key='', _value=''):
        #print _key_path,'+', _key
        if len(_key_path) <= 0 and self.global_dict.has_key(_key):
            self.global_dict[_key] = _value
            return
        kpl = _key_path.split('#')
        child_list = self.root_list[0]
        ret = self.trace_value(child_list, kpl, 0, _key, _value)
        if ret == True:
            print 'set value success!'
        else:
            print 'set value failed!'
        
    def to_lines(self):
        self.lines = []
        self.dict2lines(self.global_dict, self.lines, ':')   
        root_list = self.root_list[0]
        self.trace_lines(root_list)
        #for line in self.lines:
        #    if len(line) > 0 and line[0] == '#':
        #        continue
        #    print line
        return self.lines
    
    def trace_lines(self, _list):
        if len(_list) <= 0:
            return
        for item in _list:
            #node name
            self.lines.append(item[0])
            #node value
            self.dict2lines(item[1], self.lines, ':')
            #chd node
            self.trace_lines(item[2])
        return
    

def _test():
    uc = Ubconf(1)
    '''
    uc.get_fromfile('test_data/bs_info.conf')
    uc.set_value('[UbClientConfig]#[.UbClient]#[..@Service]:2#[...@Server]:3', 'IP', '234.123.231.145')
    uc.set_value('[UbClientConfig]#[UbClientConfig.Galileo]#[..REQUEST_RESOURCE]#[...@RES_ARR]:3', 'NAME', 'fc_cc')
    ls1 = uc.to_lines()
    f1 = open('t1', 'w')
    for l1 in ls1:
         print >> f1, l1
    f1.close()
    '''
    '''
    uc.get_fromfile('test_data/pfs.conf')
    uc.set_value('[mola]#[.@metaserver]', 'ip', '10.65.45.1')
    uc.set_value('[page_table]', 'table', 'asfsdfasd')
    
    ls2 = uc.to_lines()
    f2 = open('t2', 'w')
    for l2 in ls2:
         print >>f2, l2
    f2.close()
    '''
    '''
    uc.get_fromfile('test_data/ufs.conf') 
    uc.set_value('[UbClientConfig]#[.UbClient]#[..@Service]:2#[...@Server]', 'Port', '1234')
    uc.set_value('[UbClientConfig]#[UbClientConfig.Galileo]#[..REQUEST_RESOURCE]#[...@RES_ARR]:2', 'NAME', 'ufs_1')
    uc.set_value('[UbClientConfig]#[UbClientConfig.Galileo]#[..REQUEST_RESOURCE]#[...@RES_ARR]:2', 'ADDR', '/nova/se/ufs_1')
    ls1 = uc.to_lines()
    f1 = open('t1', 'w')
    for l1 in ls1:
         print >> f1, l1
    f1.close()
    '''
    '''
    uc.get_fromfile('test_data/di_info.conf') 
    uc.set_value('[UbClientConfig]#[.Reactor]', 'ThreadNum', '1234')
    uc.set_value('[UbClientConfig]#[.UbClient]#[..@Service]', 'Name', 'arrmoorr')
    uc.set_value('[UbClientConfig]#[.UbClient]#[..@Service]#[...@Server]', 'IP', '127.1.2.3')
    ls1 = uc.to_lines()
    f1 = open('t1', 'w')
    for l1 in ls1:
         print >> f1, l1
    f1.close() 
    '''
    uc.get_fromfile('test_data/flow_operate.conf') 
    uc.set_value('[UbClientConfig]#[.UbClient]#[..@Service]:2','DefaultConnectTimeOut','12')
    uc.set_value('[UbClientConfig]#[.test]', 'testnode', '9089')
    ls1 = uc.to_lines()
    f1 = open('t1', 'w')
    for l1 in ls1:
        print >> f1, l1
    f1.close()

if __name__ == '__main__':
    _test()

