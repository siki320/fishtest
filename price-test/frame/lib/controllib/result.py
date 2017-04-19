# -*- coding: GB18030 -*-
'''
Created on Nov 9, 2011

@author: caiyifeng<caiyifeng>

@summary: DResult����
'''

import datetime
import copy_reg
import types
import os

from frame.lib.controllib.report import DtestReport

from frame.lib.commonlib.timer import Timer
from frame.lib.commonlib.relpath import get_relpath
from frame.lib.commonlib.utils import get_py_owner, get_ejb_content
from frame.lib.commonlib.safe_encode import safegb
from frame.lib.errorlocate.result import ErrlocateResult

class DResult(object):
    FAILED = 0
    PASS = 1
    SKIP = 2

    lit_dict = {FAILED:"Failed",
                PASS:"P",
                SKIP:"Skip"
                }


    def __init__(self, report=DtestReport()):
        self.case_result_dict = {}      # <case_str, CaseResult����>�ֵ�
        self.case_time_dict = {}        # <case_str, Timer����>�ֵ�

        self.alltime = Timer()          # ��¼�ܵ�����ʱ��
        self.depot = {}                 # ���Ի��������ֵ䣬�ʺ��ڲ�ͬsuiteִ�����̵ĸ��Ի����

        self.report = report

        self.plugin_bench_timer = Timer()   # plugin benchmark������ʱ��
        self.plugin_startup_timer = Timer() # plugin startup������ʱ��

        self.start_time = datetime.datetime.now()
        self.end_time = datetime.datetime.now()

        self.errlocateResult = ErrlocateResult()
        self.total_result = True    # ���ս��

    def __add__(self, other):
        self.case_result_dict = dict(self.case_result_dict, **other.case_result_dict)
        self.case_time_dict = dict(self.case_time_dict, **other.case_time_dict)
        self.alltime = self.alltime + other.alltime
        self.depot = dict(self.depot, **other.depot)
        self.plugin_bench_timer += other.plugin_bench_timer
        self.plugin_startup_timer += other.plugin_bench_timer
        self.errlocateResult = self.errlocateResult + other.errlocateResult
        if self.start_time > other.start_time:
            self.start_time = other.start_time
        if self.end_time < other.end_time:
            self.end_time = other.end_time

        if hasattr(other, 'case_rel'):
            if not hasattr(self, 'case_rel'):
                self.case_rel = []
            self.case_rel.extend(other.case_rel)

        if hasattr(other, 'covinfo') and other.covinfo != None:
            if hasattr(self, 'covinfo') and self.covinfo != None:
                self.covinfo += other.covinfo
            else:
                self.covinfo = other.covinfo

        return self

    # ------ mutator ------
    def add_property(self, key, value):
        self.depot[key] = value
    # ------ (End) mutator ------

    # ------ accessor ------
    def get_total_result(self):
        '''@summary: �����ܽ����True or False'''
        for cr in self.case_result_dict.values():
            if cr.result == DResult.FAILED:
                self.total_result = False
                return False

        return self.total_result

    def get_casenum(self):
        return len(self.case_result_dict)

    def get_failed_casenum(self):
        return len([r for r in self.case_result_dict.values() if r.result==DResult.FAILED])

    def _get_testnum(self):
        return sum([r.get_testnum() for r in self.case_result_dict.values()] )

    def _get_failed_testnum(self):
        return sum([r.get_failed_testnum() for r in self.case_result_dict.values()] )

    def _get_case_owner(self, case_str):
        '''@summary: ��case�ļ��л�ȡcase_owner
        @note: ���case��û�й̶���ʽ��author�򣬷���unkown'''
        return get_py_owner(case_str)

    def _get_relpath(self, abspath):
        return get_relpath(abspath)
    # ------ (End) accessor ------

    # -------- DtestReport������ ---------
    def log_case_summary(self, resultpath):
        '''@summary: ��ӡcase summary��Ϣ
        @param resultpath: ���������ļ�·��'''
        return self.report.log_case_summary(self, resultpath)

    def log_times(self):
        '''@summary: ��־��¼ʱ����Ϣ'''
        self.report.log_times(self)

    def gen_json_result(self, jsonpath, sum_num, fail_num):
        '''@summary: ���json�����������ȫ����Ϣ����������Խ�����д���
        @param jsonpath: ���������ļ�·��'''
        self.report.gen_json_result_2(jsonpath,sum_num, fail_num, 0)


    def gen_junit_report(self, junitpath, level):
        '''@summary: ����junit����
        @param junitpath: ���ɵ�junit·��
        @param level: ������"case" or "test"����ʾ��ͬ�ĵȼ�'''
        self.report.gen_junit_report(self, junitpath, level)

    def gen_mail_report(self, mailpath, level, ejb=False):
        '''@summary: �����ʼ�����Ƭ��
        @attention: Ϊ�����hudson, �������Ķ���ת��Ϊutf-8
        @param mailpath: �����ʼ������·��
        @param level: "case"�� "test"����ʾ��ͬ�ĵȼ�
        @param ejb: ejbΪTrueʱ��������ȡdescription�е�EJB����'''
        self.report.gen_mail_report(self, mailpath, level, ejb)

    # -------- (End) DtestReport������ ---------

    # ==========================
    class CaseResult(object):
        '''@summary: ����case�Ľ��'''
        def __init__(self, result, detail, caseobj=None, exc_stack=None):
            self.result = result
            self.detail = detail
            self.caseobj = caseobj      # ΪNone��ʾû��case����
            if exc_stack:
                self.exc_stack = safegb(exc_stack)      # �쳣��ջ�ı�, gb-safe
            else:
                self.exc_stack = ""

            self.test_result_dict = {}  # <testname, TestResult����>�ֵ�

        # ------ mutator ------
        def add_passed_test(self, testfunc):
            self.test_result_dict[testfunc.__name__] = DResult.TestResult(testfunc, DResult.PASS)

        def add_failed_test(self, testfunc, exc_stack):
            self.test_result_dict[testfunc.__name__] = DResult.TestResult(testfunc, DResult.FAILED, excstack=exc_stack)

        def add_detail(self, d):
            if self.detail:
                self.detail += "," + d
            else:
                # ԭ��detailΪ��
                self.detail = d

        def add_excstack(self, excstack):
            excstack = safegb(excstack)

            if self.exc_stack:
                self.exc_stack += "\n" + excstack
            else:
                # ԭ��exc_stackΪ��
                self.exc_stack = excstack
        # ------ (End) mutator ------

        # ------ accessor ------
        def __str__(self):
            r'''@summary: ������־�ı�
            @return: "result \t detail \t failed_test_list", ����failed_test_list�ö��ŷָ�'''
            return "\t".join( [DResult.lit_dict[self.result], self.detail, ",".join(self.failed_tests)] )

        def str_exc_stacks(self):
            '''@summary: ����case�Լ�����test���쳣��ջ��Ϣ'''
            if self.exc_stack:
                stack_str = [self.exc_stack]
            else:
                stack_str = []

            for i,j in zip(self.failed_tests, self.test_exc_stacks):
                stack_str.append("%s:\n%s" % (i, j))

            return "\n".join(stack_str)

        def str_descs(self, ejb=False):
            '''@summary: ����case�Լ�����failed test��description'''
            self_desc = self.get_desc(ejb)
            if self_desc:
                desc_str = [self_desc]
            else:
                desc_str = []

            for tname in self.failed_tests:
                tresult = self.test_result_dict[tname]
                tdesc = tresult.get_desc(ejb)

                if tdesc:
                    desc_str.append("%s:\n%s" % (tname, tdesc))

            return "\n\n".join(desc_str)

        def get_desc(self, ejb=False):
            '''@summary: ����case������
            @param ejb: ΪTrueʱ'����'����ejb������ΪFalseʱ��������case docstring'''
            if not self.caseobj:
                return ""

            if ejb:
                content = get_ejb_content(self.caseobj.desc)
                if content:
                    return content

            # ��ejb flag������û��ejb���ݣ���������desc
            return self.caseobj.desc

        def get_testnum(self):
            return len(self.passed_tests) + len(self.failed_tests)

        def get_failed_testnum(self):
            return len(self.failed_tests)

        def get_passed_testnum(self):
            return len(self.passed_tests)
        # ------ (End) accessor ------

        # ------- �����ϵĳ�Ա���� --------
        @property
        def passed_tests(self):
            '''@summary: ����PASS��testname�б�'''
            return sorted([tname for (tname, tr) in self.test_result_dict.items() if tr.result == DResult.PASS])

        @property
        def failed_tests(self):
            '''@summary: ����FAIL��testname�б�'''
            return sorted([tname for (tname, tr) in self.test_result_dict.items() if tr.result == DResult.FAILED])

        @property
        def test_exc_stacks(self):
            '''@summary: ����fail test���쳣��ջ�ı��б�, gb-safe
            @attention: ����� failed_tests() ��˳��һ��'''
            return [self.test_result_dict[tname].excstack for tname in self.failed_tests]
        # ------- (End) �����ϵĳ�Ա�ӿ� --------

    # ========================
    class TestResult(object):
        '''@summary: ����test���'''
        def __init__(self, testfunc, result, excstack=None):
            '''@param testfunc: test��������'''
            self.testfunc = testfunc
            self.result = result
            if excstack:
                self.excstack = safegb(excstack)      # �쳣��ջ�ı�, gb-safe
            else:
                self.excstack = ""

        def get_desc(self, ejb=False):
            '''@summary: ����test������
            @param ejb: ΪTrueʱ'����'����ejb������ΪFalseʱ��������test docstring'''
            d = self.testfunc.__doc__
            if not d:
                return ""

            d = safegb(d).strip()
            line_list = [l.lstrip() for l in d.splitlines()]    # ɾ��docstringÿһ�п�ͷ�����ܵ�����
            d = "\n".join(line_list)

            if ejb:
                content = get_ejb_content(d)
                if content:
                    return content

            # ��ejb flag������û��ejb���ݣ���������desc
            return d


# ==========================
class CaseResult(object):
    '''@summary: ����case�Ľ��'''
    def __init__(self, result, detail, caseobj=None, exc_stack=None):
        self.result = result
        self.detail = detail
        self.caseobj = caseobj      # ΪNone��ʾû��case����
        if exc_stack:
            self.exc_stack = safegb(exc_stack)      # �쳣��ջ�ı�, gb-safe
        else:
            self.exc_stack = ""

        self.test_result_dict = {}  # <testname, TestResult����>�ֵ�
        self.log_record = ""

    # ------ mutator ------
    def add_passed_test(self, testfunc):
        self.test_result_dict[testfunc.__name__] = TestResult(testfunc, DResult.PASS)

    def add_failed_test(self, testfunc, exc_stack):
        self.test_result_dict[testfunc.__name__] = TestResult(testfunc, DResult.FAILED, excstack=exc_stack)

    def add_detail(self, d):
        if self.detail:
            self.detail += "," + d
        else:
            # ԭ��detailΪ��
            self.detail = d

    def add_excstack(self, excstack):
        excstack = safegb(excstack)

        if self.exc_stack:
            self.exc_stack += "\n" + excstack
        else:
            # ԭ��exc_stackΪ��
            self.exc_stack = excstack

    def add_log_record(self,log_record):
        self.log_record = log_record

    # ------ (End) mutator ------

    # ------ accessor ------
    def __str__(self):
        r'''@summary: ������־�ı�
        @return: "result \t detail \t failed_test_list", ����failed_test_list�ö��ŷָ�'''
        return "\t".join( [DResult.lit_dict[self.result], self.detail, ",".join(self.failed_tests)] )

    def str_exc_stacks(self):
        '''@summary: ����case�Լ�����test���쳣��ջ��Ϣ'''
        if self.exc_stack:
            stack_str = [self.exc_stack]
        else:
            stack_str = []

        for i,j in zip(self.failed_tests, self.test_exc_stacks):
            stack_str.append("%s:\n%s" % (i, j))

        return "\n".join(stack_str)

    def str_descs(self, ejb=False):
        '''@summary: ����case�Լ�����failed test��description'''
        self_desc = self.get_desc(ejb)
        if self_desc:
            desc_str = [self_desc]
        else:
            desc_str = []

        for tname in self.failed_tests:
            tresult = self.test_result_dict[tname]
            tdesc = tresult.get_desc(ejb)

            if tdesc:
                desc_str.append("%s:\n%s" % (tname, tdesc))

        return "\n\n".join(desc_str)

    def get_desc(self, ejb=False):
        '''@summary: ����case������
        @param ejb: ΪTrueʱ'����'����ejb������ΪFalseʱ��������case docstring'''
        if hasattr(self,'desc'):
            return self.desc

        if not self.caseobj:
            return ""

        if self.caseobj.__doc__ != None:
            self.caseobj.desc = self.caseobj.__doc__

        if ejb:
            content = get_ejb_content(self.caseobj.desc)
            if content:
                return content

        # ��ejb flag������û��ejb���ݣ���������desc
        return self.caseobj.desc

    def get_testnum(self):
        return len(self.passed_tests) + len(self.failed_tests)

    def get_failed_testnum(self):
        return len(self.failed_tests)

    def get_passed_testnum(self):
        return len(self.passed_tests)
    # ------ (End) accessor ------

    # ------- �����ϵĳ�Ա���� --------
    @property
    def passed_tests(self):
        '''@summary: ����PASS��testname�б�'''
        return sorted([tname for (tname, tr) in self.test_result_dict.items() if tr.result == DResult.PASS])

    @property
    def failed_tests(self):
        '''@summary: ����FAIL��testname�б�'''
        return sorted([tname for (tname, tr) in self.test_result_dict.items() if tr.result == DResult.FAILED])

    @property
    def test_exc_stacks(self):
        '''@summary: ����fail test���쳣��ջ�ı��б�, gb-safe
        @attention: ����� failed_tests() ��˳��һ��'''
        return [self.test_result_dict[tname].excstack for tname in self.failed_tests]
    # ------- (End) �����ϵĳ�Ա�ӿ� --------

    def __getstate__(self):
        '''
        this is to work around multiple case with the same name cannot be pickle issue
        just to delete the caseobj
        '''
        pickle_dict = {}
        pickle_dict['result'] = self.result
        if not hasattr(self, 'desc'):
            pickle_dict['desc'] = self.str_descs()
        else:
            pickle_dict['desc'] = self.desc
        pickle_dict['exc_stack'] = self.exc_stack
        pickle_dict['detail'] = self.detail
        pickle_dict['test_result_dict'] = self.test_result_dict
        if hasattr(self, 'covinfo'):
            pickle_dict['covinfo'] = self.covinfo
        if hasattr(self, 'case_rel'):
            pickle_dict['case_rel'] = self.case_rel
        return pickle_dict

    def __setstate__(self, dict):
        self.desc = dict['desc']
        self.result = dict['result']
        self.exc_stack = dict['exc_stack']
        self.detail = dict['detail']
        self.test_result_dict = dict['test_result_dict']
        if dict.has_key('case_rel'):
            self.case_rel = pickle_dict['case_rel']
        if dict.has_key('covinfo'):
            self.covinfo = pickle_dict['covinfo']

# ========================
class TestResult(object):
    '''@summary: ����test���'''
    def __init__(self, testfunc, result, excstack=None):
        '''@param testfunc: test��������'''
        self.testfunc = testfunc
        self.result = result
        if excstack:
            self.excstack = safegb(excstack)      # �쳣��ջ�ı�, gb-safe
        else:
            self.excstack = ""

    def get_desc(self, ejb=False):
        '''@summary: ����test������
        @param ejb: ΪTrueʱ'����'����ejb������ΪFalseʱ��������test docstring'''
        if hasattr(self,'desc'):
            return self.desc
        d = self.testfunc.__doc__
        if not d:
            return ""

        d = safegb(d).strip()
        line_list = [l.lstrip() for l in d.splitlines()]    # ɾ��docstringÿһ�п�ͷ�����ܵ�����
        d = "\n".join(line_list)

        if ejb:
            content = get_ejb_content(d)
            if content:
                return content

        # ��ejb flag������û��ejb���ݣ���������desc
        return d

    def __getstate__(self):
        pickle_dict = {}
        if not hasattr(self, 'desc'):
            pickle_dict['desc'] = self.get_desc()
        else:
            pickle_dict['desc'] = self.desc
        pickle_dict['result'] = self.result
        pickle_dict['excstack'] = self.excstack
        return pickle_dict

    def __setstate__(self, dict):
        self.result = dict['result']
        self.desc = dict['desc']
        self.excstack = dict['excstack']

def _pickle_method(method):
    func_name = method.im_func.__name__
    obj = method.im_self
    cls = method.im_class
    if func_name.startswith('__') and not func_name.endswith('__'):
        #deal with mangled names
        cls_name = cls.__name__.lstrip('_')
        func_name = '_%s%s' % (cls_name, func_name)
    return _unpickle_method, (func_name, obj, cls)

def _unpickle_method(func_name, obj, cls):
    if obj and func_name in obj.__dict__:
        cls, obj = obj, None # if func_name is classmethod
    for cls in cls.__mro__:
        try:
            func = cls.__dict__[func_name]
        except KeyError:
            pass
        else:
            break
    return func.__get__(obj, cls)

def savemodule(module):
    return loadmodule, (module.__name__,)

def loadmodule(modulename):
    import sys
    sys.path.append(os.path.join(sys.path[0],"../errorlocating"))
    sys.path.append(os.path.join(sys.path[0],"../../errorlocating"))
    print os.path.join(sys.path[0],"../errorlocating")
    return __import__(modulename.split('.')[-1])

copy_reg.pickle(types.MethodType, _pickle_method, _unpickle_method)
copy_reg.pickle(types.ModuleType, savemodule)

def dump_result(result,pickle_path):
    import pickle
    pickle.dump(result, open(pickle_path, 'w'))

def load_result(pickle_path):
    import pickle
    return pickle.load(open(pickle_path))

