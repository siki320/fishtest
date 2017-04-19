# -*- coding: GB18030 -*-
'''
Created on Nov 9, 2011

@author: caiyifeng<caiyifeng>

@summary: ����case�Ļ���
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
        self.ignore_list = []   # �����б�
        self.tags = []          # tags�б�ÿ��Ԫ�ػ���һ���б�; ���б��ڲ������ϵ�����б�֮�䣬���ϵ
        self.testname = "."     # testname����
        self.prior = CasePriority.DEFAULT
        self.author = ""
        
    def read_ignore_list(self, filepath):
        f = open(filepath)
        for line in f:
            line = line.rstrip()
            if line != '':
                abs_path = os.path.abspath(line)    # line�ȿ����Ǿ���·����Ҳ���������������Ŀ¼�����·��
                self.ignore_list.append(abs_path)
        f.close()
        
    def parse_tag(self, tag_str):
        '''@summary: ����tagѡ��'''
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
        @summary: ��args�е�DtestCase����suite�����ҵݹ鴦����Ŀ¼
        @param suite: DtestSuite����
        @param result: DResult����������¼pick�����еĽ��
        '''
        for arg in args:
            spec_tests = []
            if arg.find(":")>=0: #ͨ���ַ���ָ�������testFunction����,�ָ�
                arg,spec_test = arg.split(":")
                spec_tests = spec_test.split(",")

            arg = os.path.abspath(arg)
            relarg = self._get_relpath(arg)
            base = os.path.basename(arg)
            modulename, ext = os.path.splitext(base)
            if os.path.isfile(arg) and ext == ".py" and modulename != "__init__":
                # ��python�ļ����Ҳ���__init__.py
                
                # ����case
                ignored = False
                for i in self.ignore_list:
                    if arg.startswith(i):
                        # case·����ǰ׺���Ϲ�����
                        ignored = True
                        break
                        
                if ignored:
                    dlog.debug("'%s' starts with ignore line. Ignore it", relarg)
                    result.case_result_dict[relarg] = CaseResult(result.SKIP, "Ignored")
                    continue
               
                #ֻ����ָ��author��case
                if self.author != "": 
                    if get_py_owner(arg) != self.author:
                        continue
                # �����ģ��
                try:
                    amod, modulename = self._myimport(arg, modulename)
                except Exception:
                    # ���ɵ����pythonģ�飬����
                    dlog.error("Can't import module : %s. Skip it", relarg, exc_info=True)
                    result.case_result_dict[relarg] = CaseResult(result.FAILED, "Syntax_Error", exc_stack=traceback.format_exc())
                    continue
                
                # ��ȡģ���еĲ�����
                test_cls_flag = False
                for item in amod.__dict__.keys():
                    #ȷ����class & ȷ����DtestCase���� & ȷ�����ڸ�ģ��
                    if inspect.isclass(amod.__dict__[item]) and \
                            issubclass(amod.__dict__[item], DtestCase) and \
                                    amod.__dict__[item].__dict__['__module__'] == modulename:
                        modclass = amod.__dict__[item]
                        test_cls_flag = True
                        break
                
                #ָ��ģ���ļ���û�л�ȡ��������
                if not test_cls_flag:
                    dlog.warning("No test class found in '%s'. Ignore this file", modulename + '.py')
                    result.case_result_dict[relarg] = CaseResult(result.SKIP, "No_Case")
                    continue
                                   
                # ʵ����Case��
                try:
                    acase = modclass()
                    acase.set_filepath(arg)
                    acase.set_desc(amod.__doc__)
                except Exception:
                    # ʵ��������
                    dlog.error("Can't instance class : %s. Skip it", relarg, exc_info=True)
                    result.case_result_dict[relarg] = CaseResult(result.FAILED, "Syntax_Error", exc_stack=traceback.format_exc())
                    continue

                if acase.priority&self.prior == 0:
                    dlog.debug("'%s' is not picked becuase of proirioty", relarg)
                    continue
                
                # ���˲���enable��case
                if not acase.enable:
                    dlog.debug("'%s' is not enable. Ignore it", relarg)
                    result.case_result_dict[relarg] = CaseResult(result.SKIP, "Disable")
                    continue
                
                # ���˲�����tag��case
                if not self._check_meet_tag(acase.tags):
                    dlog.debug("'%s' doesn't meet tags. Ignore it", relarg)
                    result.case_result_dict[relarg] = CaseResult(result.SKIP, "Tag_Filter")
                    continue
                
                # �õ�case������testXXX����
                tests = []
                prior_que = acase.tests_bvt+acase.tests_high+acase.tests_low
                for propname in dir(acase):
                    if propname.startswith("test"):
                        # ��test��ͷ������
                        prop = getattr(acase, propname)
                        if not isinstance(prop, instancemethod):
                            # prop����ʵ������
                            continue
                        if not prior_que:
                            #����ûָ���κ�case������ǰ�ķ�ʽһ������
                            tests.append(prop)
                            continue

                        if propname not in prior_que:
                            # ĳ��testû�б���¼���κζ���,�����slowĬ�϶���
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
                            
                #û���������ȼ����е�case�Ƿ���testXXX����
                if not prior_que and not tests:
                    dlog.error("Class '%s' has no testXXX method. Skip it", relarg)
                    result.case_result_dict[relarg] = CaseResult(result.FAILED, "No_Test_Method")
                    continue

                # ����testnameѡ��tests
                f_tests = [t for t in tests if re.search(self.testname, t.__name__)]

                if len(spec_tests) > 0: #ָ��test�б�ֻ����ָ���б�
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
                
 
                # ��case����suite
                suite.addcase(acase)
                
                # ��case��Ӧ��test��������suite
                suite.add_test_dict(acase, f_tests)
                
            elif os.path.isdir(arg):
                # ����Ŀ¼���ݹ鴦��
                subargs = os.listdir(arg)
                subargs.sort()      # ȷ��case��ִ��˳��̶�
                self.pickcases([arg+'/'+subarg for subarg in subargs], suite, result)
                
            elif not os.path.exists(arg):
                # �ļ�������
                dlog.error("Case doesn't exist : %s. Skip it", relarg)
                result.case_result_dict[relarg] = CaseResult(result.FAILED, "Not_Exist")
                
                
    def _get_relpath(self, abspath):
        return get_relpath(abspath)
        
    def _myimport(self, abspath, modulename):
        '''
        @summary: ����caseģ��
        @param abspath: case����·��
        @param modulename: ģ����
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
        '''@summary: ���case_tags�Ƿ����tags'''
        # û��ָ��tags����������case
        if not self.tags:
            return True
        
        for tag in self.tags:
            # ���tag��case_tags�н���
            tag_set = set(tag)
            case_tags_set = set(case_tags)
            
            if not (tag_set & case_tags_set):
                # û�н�����������Ҫ��
                return False
        else:
            return True
                
