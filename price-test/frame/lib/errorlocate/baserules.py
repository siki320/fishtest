# -*- coding: GB18030 -*-
'''
Created on May 18, 2012

@author: caiyifeng<caiyifeng>
'''

import re

from frame.lib.commonlib.dlog import dlog
from frame.lib.commonlib.utils import get_py_owner

class errInstance(object):
    '''@summary: 纯文本信息，记录错误定位的结果'''
    def __init__(self, person, reason, keyinfo=None):
        # 结果定位信息
        self.responsible_person = person
        self.reason = reason
        
        if keyinfo:
            # 复制keyinfo信息
            self.failed_case_list = keyinfo.get_casename_list()     # case名列表，case名 = "case相对路径 .fail_stage"
            self.module = keyinfo.module
        
        
class base_rule(object):
    "base class for rules"
    def __init__(self):
        self.errlist = []
        
    def module_match(self, keyinfo):
        return (True if self.module == keyinfo.module or self.module == 'PUBLIC' else False)
        

# ===== 以下是通用规则集 =====
class RULE_assert_failed(base_rule):
    "Case Assert Failed"
    module = 'PUBLIC'
    def match(self, keyinfo):
        # 匹配未命中, 返回False
        if re.search("AssertionError", keyinfo.testException) is None:
            return False
        
        # ！！断言：用于test失败验证，因此keyinfo只会有一个case
        case = keyinfo.cases[0]
        owner = get_py_owner(case)
        if owner == '':
            owner = "This Author is lazy,  name is not left!"
        if owner not in [e.responsible_person for e in self.errlist] or \
            keyinfo.module not in [e.module for e in self.errlist]:
            # 匹配命中, 存储err实例信息
            err = errInstance(owner, self.__doc__, keyinfo)
            self.errlist.append(err)
        else:
            l = filter(lambda x:x.responsible_person == owner and x.module == keyinfo.module, self.errlist)
            if len(l) != 1:
                dlog.error("Find two responsible person in one rule")
            else:
                l[0].failed_case_list.extend(keyinfo.get_casename_list())
        
        return True
        

class RULE_cfg_missing(base_rule):
    "These Files Missing such Configs "
    module = 'PUBLIC'
    def match(self, keyinfo):
        # 匹配未命中, 返回False
        if len(keyinfo.cfgMissing) == 0:
            return False
        
        # 匹配命中, 存储err实例信息
        err = errInstance("unknown", self.__doc__+'\n\t'+'\n\t'.join(keyinfo.cfgMissing), keyinfo)
        self.errlist.append(err)
        return True


class RULE_file_missing(base_rule):
    "Missing Data Files"
    module = 'PUBLIC'
    def match(self, keyinfo):
        # 匹配未命中, 返回False
        if len(keyinfo.fileMissing) == 0:
            return False
        
        # 匹配命中, 存储err实例信息
        err = errInstance("unknown", self.__doc__+'\n\t'+'\n\t'.join(keyinfo.fileMissing), keyinfo)
        self.errlist.append(err)
        return True    


class RULE_dir_empty(base_rule):
    "No file in these Dirs"
    module = 'PUBLIC'
    def match(self, keyinfo):
        # 匹配未命中, 返回False
        if len(keyinfo.emptyDir) == 0:
            return False
        
        # 匹配命中, 存储err实例信息
        err = errInstance("unknown", self.__doc__+'\n\t'+'\n\t'.join(keyinfo.emptyDir), keyinfo)
        self.errlist.append(err)
        return True

class RULE_no_such_directory(base_rule):
    "No such directory in current ENV, Maybe SVN co Failed!"
    module = 'PUBLIC'
    def match(self, keyinfo):
        # 匹配未命中, 返回False
        if not re.search('IOError', keyinfo.startException):
            return False
        
        fpath = ""
        for line in keyinfo.startException.split('\n'):
            if 'IOError' not in line:
                continue
            fpath = re.search("\'\/.*\'",line).group()[1:-1]
            break
        
        dir_path, fname = os.path.split(fpath)
        while len(dir_path) > 0:
            if not os.path.isdir(dir_path):
                parent_dir, _dir = os.path.split(dir_path)
                if os.path.isdir(parent_dir):
                    break
                else:
                    dir_path = parent_dir
        # 匹配命中, 存储err实例信息
        err = errInstance("Unknown", self.__doc__ + '\n\t' + dir_path, keyinfo)
        self.errlist.append(err)
        return True 
