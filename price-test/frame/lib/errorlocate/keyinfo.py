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
    '''@summary: 配置文件中的一行'''
    def __init__(self, module, fpath, _type="PATH", seg=":"):
        self.module = module
        self.fpath = fpath
        self.cfg_list = []
        self.seg = seg
        self._type = _type      # 配置项的类型,这里分为路径类和非路径类('PATH' or 'NON_PATH')

class BaseKeyinfo(object):
    '''@summary: 错误排查的关键信息'''
    def __init__(self):
        self.cases = []                 # keyinfo对应的case obj list
        self.failed_step = ""           # 存储case失败的阶段
        self.startException = ""        # 启动阶段的exception
        self.testException = ""         # 测试阶段的exception
        self.fileMissing = []           # 缺失信息
        self.cfgMissing = []
        self.emptyDir = []
        
        # 非失败相关信息
        # （常量）由子类定义时设置
        self.module = ""            # 被测的模块名
        self.rulemodule = None      # 相应的rule class所在的python模块对象
        
    def get_casename_list(self):
        '''@summary: 返回case名列表，case名 = case相对路径 .fail_stage'''
        return [get_relpath(acase)+"."+self.failed_step for acase in self.cases]
    
    def missing_check(self, module_path_dict):
        '''@summary: 获取missing信息，填写到 fileMissing, cfgMissing, emptyDir中
        @param module_path_dict: 相关的module安装绝对路径'''
        from os.path import abspath
        
        for _key, _list in self.check_dict.items():
            # 获得一个check流
            for _unit in _list:
                module = module_path_dict[_unit.module]
                confPath = module + "/" + _unit.fpath
                seg = _unit.seg
                if not os.path.exists(confPath):
                    self.fileMissing.append( get_relpath(abspath(confPath)) )
                    break
                
                kvfile = Kvconf(confPath, seg)
    
                # 检查该单元需要检测的配置项是否配置
                confMissed = False
                for cfg in _unit.cfg_list:
                    if not kvfile.haskey(cfg):
                        confMissed = True
                        self.cfgMissing.append(_unit.module + ' : ' +_unit.fpath+ " -> " + cfg)
    
                # 如果缺少某个配置项，则不用继续检查上游模块, 直接break该check流
                if confMissed:
                    break
                
                # 判断该单元的类型, 路径类or非路径类, 非路径类则check完成, 继续下一个单元
                if _unit._type == "NON_PATH":
                    break
                elif _unit._type == "PATH":
                    pass
                else:
                    dlog.warning("Got wrong type in Keyinfo module: %s", _unit._type)
                    break
                
                # 若为路径类, 则继续判断路径所对应的文件是否存在
                check_path = module
                using = None
                continue_flag = False
                for cfg in _unit.cfg_list:
                    if using == None:
                        check_path += "/" + kvfile.getvalue(cfg)
                    else:
                        check_path += "/" + using + "/"+kvfile.getvalue(cfg)
    
                    # 依次检查目录，文件
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
    
                    # 重置using
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
                        
                # check本条规则ok, 则直接进行下一个check流, 不再追述本条check流的上游模块
                if continue_flag :
                    continue
                else:
                    break
        
    def make_check_flow(self, module_name, missing_conf):
        '''@summary: 从missing_conf中读取检查链
        @param module_name: missing_conf中的模块名
        @param missing_conf: 文件路径
        @return: 检查链字典'''
        # 产出的check_dict结构如下：
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
                
                if line == "" or line.startswith("#"):  # 空行 or 注释行，忽略
                    continue
                
                if module_split == line: # 匹配到模块对应的conf区域, 置位读取标志
                    insert = True
                elif '[' in line and '@' not in line: # 非模块对应conf区域
                    insert = False
                elif '[.@' in line and insert: # 读取check flow
                    _key = re.search('\w+', line).group()
                    check_dict[_key] = []
                elif insert : # 读取配置单元
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
        '''@summary: 获得一个字典，字典中必须有'order'键'''
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
    
