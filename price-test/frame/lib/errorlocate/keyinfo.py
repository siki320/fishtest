# -*- coding: GB18030 -*-
'''
Created on May 18, 2012

@author: caiyifeng<caiyifeng>
'''

import os
import re

from frame.lib.commonlib.kvconf import Kvconf
from frame.lib.commonlib.dlog import dlog
from frame.lib.commonlib.relpath import get_relpath


class cfg_unit(object):
    '''@summary: �����ļ��е�һ��'''
    def __init__(self, module, fpath, _type="PATH", seg=":"):
        self.module = module
        self.fpath = fpath
        self.cfg_list = []
        self.seg = seg
        self._type = _type      # �����������,�����Ϊ·����ͷ�·����('PATH' or 'NON_PATH')

class BaseKeyinfo(object):
    '''@summary: �����Ų�Ĺؼ���Ϣ'''
    def __init__(self):
        self.cases = []                 # keyinfo��Ӧ��case obj list
        self.failed_step = ""           # �洢caseʧ�ܵĽ׶�
        self.startException = ""        # �����׶ε�exception
        self.testException = ""         # ���Խ׶ε�exception
        self.fileMissing = []           # ȱʧ��Ϣ
        self.cfgMissing = []
        self.emptyDir = []
        
        # ��ʧ�������Ϣ
        # �������������ඨ��ʱ����
        self.module = ""            # �����ģ����
        self.rulemodule = None      # ��Ӧ��rule class���ڵ�pythonģ�����
        
    def get_casename_list(self):
        '''@summary: ����case���б�case�� = case���·�� .fail_stage'''
        return [get_relpath(acase)+"."+self.failed_step for acase in self.cases]
    
    def missing_check(self, module_path_dict):
        '''@summary: ��ȡmissing��Ϣ����д�� fileMissing, cfgMissing, emptyDir��
        @param module_path_dict: ��ص�module��װ����·��'''
        from os.path import abspath
        
        for _key, _list in self.check_dict.items():
            # ���һ��check��
            for _unit in _list:
                module = module_path_dict[_unit.module]
                confPath = module + "/" + _unit.fpath
                seg = _unit.seg
                if not os.path.exists(confPath):
                    self.fileMissing.append( get_relpath(abspath(confPath)) )
                    break
                
                kvfile = Kvconf(confPath, seg)
    
                # ���õ�Ԫ��Ҫ�����������Ƿ�����
                confMissed = False
                for cfg in _unit.cfg_list:
                    if not kvfile.haskey(cfg):
                        confMissed = True
                        self.cfgMissing.append(_unit.module + ' : ' +_unit.fpath+ " -> " + cfg)
    
                # ���ȱ��ĳ����������ü����������ģ��, ֱ��break��check��
                if confMissed:
                    break
                
                # �жϸõ�Ԫ������, ·����or��·����, ��·������check���, ������һ����Ԫ
                if _unit._type == "NON_PATH":
                    break
                elif _unit._type == "PATH":
                    pass
                else:
                    dlog.warning("Got wrong type in Keyinfo module: %s", _unit._type)
                    break
                
                # ��Ϊ·����, ������ж�·������Ӧ���ļ��Ƿ����
                check_path = module
                using = None
                continue_flag = False
                for cfg in _unit.cfg_list:
                    if using == None:
                        check_path += "/" + kvfile.getvalue(cfg)
                    else:
                        check_path += "/" + using + "/"+kvfile.getvalue(cfg)
    
                    # ���μ��Ŀ¼���ļ�
                    if os.path.isdir(check_path):
                        _dir = os.listdir(check_path)
                        if len(_dir) == 0 or (len(_dir)== 1 and '.svn' in _dir):
                            self.emptyDir.append( get_relpath(abspath(check_path)) + '/')
                            continue_flag = True
                            break
                    else:
                        if not os.path.exists(check_path):
                            self.fileMissing.append( get_relpath(abspath(check_path)) )
                            continue_flag = True
                            break
    
                    # ����using
                    if os.path.exists(check_path+"/using"):
                        f = open(check_path+"/using",'r')
                        try:
                            using=f.read()
                            _dir = os.listdir(check_path + '/' + using)
                            if len(_dir) == 0 or (len(_dir)== 1 and '.svn' in _dir) :
                                self.emptyDir.append( get_relpath(abspath(check_path + '/' + using)) + '/')
                                continue_flag = True
                                break
                        finally:
                            f.close()
                    else:
                        using = None
                        
                # check��������ok, ��ֱ�ӽ�����һ��check��, ����׷������check��������ģ��
                if continue_flag :
                    continue
                else:
                    break
        
    def make_check_flow(self, module_name, missing_conf):
        '''@summary: ��missing_conf�ж�ȡ�����
        @param module_name: missing_conf�е�ģ����
        @param missing_conf: �ļ�·��
        @return: ������ֵ�'''
        # ������check_dict�ṹ���£�
        #     {
        #        'Flow1' ([.@Flow1]):
        #            [
        #                cfg_unit(
        #                    'module': 'BDBS',
        #                    'fpath': './conf/startup/business.conf',
        #                    'cfg_list': ['ct_feature_base_dir', 'ct_feature_base_metainfo_file'],
        #                    '_type': 'PATH',
        #                    'seg': ':'
        #                ),
        #                ...
        #            ],
        #         'Flow2': ...
        #     }
        check_dict = {}
        module_split = '[' + module_name + ']'
        insert = False
        
        with open(missing_conf, 'r') as fp:
            for line in fp:
                line = line.strip()
                
                if line == "" or line.startswith("#"):  # ���� or ע���У�����
                    continue
                
                if module_split == line: # ƥ�䵽ģ���Ӧ��conf����, ��λ��ȡ��־
                    insert = True
                elif '[' in line and '@' not in line: # ��ģ���Ӧconf����
                    insert = False
                elif '[.@' in line and insert: # ��ȡcheck flow
                    _key = re.search('\w+', line).group()
                    check_dict[_key] = []
                elif insert : # ��ȡ���õ�Ԫ
                    token = line.split('\t')
                    if 0 < len(token) < 5 :
                        dlog.warning("Got mistake in %s:\n%s", missing_conf, line)
                        continue
                    u = cfg_unit(token[0], token[1], token[3], token[4])
                    k = token[2].split(',')
                    u.cfg_list.extend(k)
                    check_dict[_key].append(u)
                else:
                    continue

        return check_dict
    
    def getInfo(self):
        '''@summary: ���һ���ֵ䣬�ֵ��б�����'order'��'''
        _dict = {}
        _dict['order'] = [
                          "File Missing", 
                          "Cfg Missing",
                          "Empty Dir",
                          "Start Exception", 
                          "Test Exception" 
                          ]
        
        if self.fileMissing:
            _dict["File Missing"] = self.fileMissing
        if self.cfgMissing:
            _dict["Cfg Missing"] = self.cfgMissing
        if self.emptyDir:
            _dict["Empty Dir"] = self.emptyDir
        if self.startException:
            _dict["Start Exception"] = self.startException
        if self.testException:
            _dict["Test Exception"] = self.testException
        
        return _dict
            
def _test_make_check_flow():
    conf_sample = os.path.abspath(os.path.dirname(__file__))+"/missing_check_sample.conf"
    
    with open(conf_sample) as fp:
        print fp.read()
        print
    
    info = BaseKeyinfo()
    check_dict = info.make_check_flow("BS", conf_sample)
    for flow in check_dict:
        print flow
        for unit in check_dict[flow]:
            print vars(unit)
        print
        
if __name__ == "__main__":
    _test_make_check_flow()
    
