# -*- coding: GB18030 -*-
'''
Created on Nov 9, 2011

@author: caiyifeng<caiyifeng>

@summary: 加载case的基类
'''

import os
import re
import inspect
import imp
import traceback
import sys
from new import instancemethod
from frame.lib.controllib.case import DtestCase,CasePriority
from frame.lib.commonlib.dlog import dlog
from frame.lib.commonlib.relpath import get_relpath
from frame.lib.controllib.result import CaseResult
from frame.lib.commonlib.utils import get_py_owner

class CasePicker(object):
    def __init__(self):
        self.ignore_list = []   # 过滤列表
        self.tags = []          # tags列表，每个元素还是一个列表; 子列表内部，或关系；子列表之间，与关系
        self.testname = "."     # testname正则
        self.prior = CasePriority.DEFAULT
        self.author = ""
        
    def read_ignore_list(self, filepath):
        f = open(filepath)
        for line in f:
            line = line.rstrip()
            if line != '':
                abs_path = os.path.abspath(line)    # line既可以是绝对路径，也可以是相对于启动目录的相对路径
                self.ignore_list.append(abs_path)
        f.close()
        
    def parse_tag(self, tag_str):
        '''@summary: 解析tag选项'''
        list_ = tag_str.split(",")
        self.tags.append([s.strip() for s in list_])
        
    def set_testname(self, testname):
        self.testname = testname

    def set_priority(self, str_priority):
        self.prior = CasePriority.str2value(str_priority)

    def set_author(self, author):
        self.author = author

    def pickcases(self, args, suite, result):
        '''
        @summary: 将args中的DtestCase加入suite，并且递归处理子目录
        @param suite: DtestSuite对象
        @param result: DResult对象，用来记录pick过程中的结果
        '''
        for arg in args:
            spec_tests = []
            if arg.find(":")>=0: #通过字符串指定具体的testFunction，以,分隔
                arg,spec_test = arg.split(":")
                spec_tests = spec_test.split(",")

            arg = os.path.abspath(arg)
            relarg = self._get_relpath(arg)
            base = os.path.basename(arg)
            modulename, ext = os.path.splitext(base)
            if os.path.isfile(arg) and ext == ".py" and modulename != "__init__":
                # 是python文件，且不是__init__.py
                
                # 过滤case
                ignored = False
                for i in self.ignore_list:
                    if arg.startswith(i):
                        # case路径的前缀符合过滤行
                        ignored = True
                        break
                        
                if ignored:
                    dlog.debug("'%s' starts with ignore line. Ignore it", relarg)
                    result.case_result_dict[relarg] = CaseResult(result.SKIP, "Ignored")
                    continue
               
                #只加载指定author的case
                if self.author != "": 
                    if get_py_owner(arg) != self.author:
                        continue
                # 导入该模块
                try:
                    amod, modulename = self._myimport(arg, modulename)
                except Exception:
                    # 不可导入的python模块，跳过
                    dlog.error("Can't import module : %s. Skip it", relarg, exc_info=True)
                    result.case_result_dict[relarg] = CaseResult(result.FAILED, "Syntax_Error", exc_stack=traceback.format_exc())
                    continue
                
                # 获取模块中的测试类
                test_cls_flag = False
                for item in amod.__dict__.keys():
                    #确认是class & 确认是DtestCase子类 & 确认属于该模块
                    if inspect.isclass(amod.__dict__[item]) and \
                            issubclass(amod.__dict__[item], DtestCase) and \
                                    amod.__dict__[item].__dict__['__module__'] == modulename:
                        modclass = amod.__dict__[item]
                        test_cls_flag = True
                        break
                
                #指定模块文件中没有获取到测试类
                if not test_cls_flag:
                    dlog.warning("No test class found in '%s'. Ignore this file", modulename + '.py')
                    result.case_result_dict[relarg] = CaseResult(result.SKIP, "No_Case")
                    continue
                                   
                # 实例化Case类
                try:
                    acase = modclass()
                    acase.set_filepath(arg)
                    acase.set_desc(amod.__doc__)
                except Exception:
                    # 实例化出错
                    dlog.error("Can't instance class : %s. Skip it", relarg, exc_info=True)
                    result.case_result_dict[relarg] = CaseResult(result.FAILED, "Syntax_Error", exc_stack=traceback.format_exc())
                    continue

                if acase.priority&self.prior == 0:
                    dlog.debug("'%s' is not picked becuase of proirioty", relarg)
                    continue
                
                # 过滤不是enable的case
                if not acase.enable:
                    dlog.debug("'%s' is not enable. Ignore it", relarg)
                    result.case_result_dict[relarg] = CaseResult(result.SKIP, "Disable")
                    continue
                
                # 过滤不符合tag的case
                if not self._check_meet_tag(acase.tags):
                    dlog.debug("'%s' doesn't meet tags. Ignore it", relarg)
                    result.case_result_dict[relarg] = CaseResult(result.SKIP, "Tag_Filter")
                    continue
                
                # 得到case的所有testXXX方法
                tests = []
                prior_que = acase.tests_bvt+acase.tests_high+acase.tests_low
                for propname in dir(acase):
                    if propname.startswith("test"):
                        # 以test开头的属性
                        prop = getattr(acase, propname)
                        if not isinstance(prop, instancemethod):
                            # prop不是实例方法
                            continue
                        if not prior_que:
                            #队列没指定任何case，和以前的方式一样处理
                            tests.append(prop)
                            continue

                        if propname not in prior_que:
                            # 某个test没有被收录到任何队列,则加入slow默认队列
                            acase.tests_low.append(propname)

                        if propname in acase.tests_bvt:
                            if self.prior & CasePriority.BVT:
                                tests.append(prop)
                                continue
                        if propname in acase.tests_high: 
                            if self.prior & CasePriority.HIGH:
                                tests.append(prop)
                                continue
                        if propname in acase.tests_low:
                            if self.prior & CasePriority.LOW:
                                tests.append(prop)
                                continue
                            
                #没有设置优先级队列的case是否含有testXXX方法
                if not prior_que and not tests:
                    dlog.error("Class '%s' has no testXXX method. Skip it", relarg)
                    result.case_result_dict[relarg] = CaseResult(result.FAILED, "No_Test_Method")
                    continue

                # 根据testname选择tests
                f_tests = [t for t in tests if re.search(self.testname, t.__name__)]

                if len(spec_tests) > 0: #指定test列表，只运行指定列表
                    f_tests=[]
                    for testname in spec_tests:
                        if not propname.startswith("test"):
                            dlog.error("testname '%s' is not start with test",testname)
                            continue
                        prop = getattr(acase, testname)
                        if not isinstance(prop, instancemethod):
                            dlog.error("testname '%s' not a instancemethod",testname)
                            continue 
                        f_tests.append(prop)

                if not f_tests:
                    dlog.debug("Class '%s' has no matching testXXX method. Skip it", relarg)
                    result.case_result_dict[relarg] = CaseResult(result.SKIP, "Testname_Filter")
                    continue
                
 
                # 将case加入suite
                suite.addcase(acase)
                
                # 将case对应的test方法加入suite
                suite.add_test_dict(acase, f_tests)
                
            elif os.path.isdir(arg):
                # 是子目录，递归处理
                subargs = os.listdir(arg)
                subargs.sort()      # 确保case的执行顺序固定
                self.pickcases([arg+'/'+subarg for subarg in subargs], suite, result)
                
            elif not os.path.exists(arg):
                # 文件不存在
                dlog.error("Case doesn't exist : %s. Skip it", relarg)
                result.case_result_dict[relarg] = CaseResult(result.FAILED, "Not_Exist")
                
                
    def _get_relpath(self, abspath):
        return get_relpath(abspath)
        
    def _myimport(self, abspath, modulename):
        '''
        @summary: 导入case模块
        @param abspath: case绝对路径
        @param modulename: 模块名
        '''
        fp, pathname, description = imp.find_module(modulename, [os.path.dirname(abspath)])
        i = 0
        while sys.modules.has_key(modulename):
            i += 1
            modulename += '_%d' % i
        m = imp.load_module(modulename, fp, pathname, description)
        fp.close()
        
        return m, modulename
    
    def _check_meet_tag(self, case_tags):
        '''@summary: 检查case_tags是否符合tags'''
        # 没有指定tags，运行所有case
        if not self.tags:
            return True
        
        for tag in self.tags:
            # 检查tag和case_tags有交集
            tag_set = set(tag)
            case_tags_set = set(case_tags)
            
            if not (tag_set & case_tags_set):
                # 没有交集，不满足要求
                return False
        else:
            return True
                
