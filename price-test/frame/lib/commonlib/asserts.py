# -*- coding: GB18030 -*-
'''
Created on Aug 30, 2011

@author: caiyifeng<caiyifeng>

@summary: ���Ժ������� ������assert & expect 
'''

import sys
import traceback
from frame.lib.commonlib import checker
#import hashlib
import commands


# ===== expect ��� =======
# ȫ�ֱ�����list of �쳣��ջ�ַ���
exclist = []

def clear_exclist():
    '''@summary: ���ȫ��exclist'''
    global exclist
    del exclist[:]
    
def str_exclist():
    '''@summary: ��exclist�ı���'''
    global exclist
    return "\n".join(exclist)
    
class ExpectError(AssertionError):
    '''��װ AssertionError����������'''
    pass
    
def wrap_expect(func):
    '''@summary: expect��װ����������һ�����׳��쳣�Ķ��Ժ���
    @note: �쳣����¼��ȫ�ֵ�exclist��'''
    if isinstance(func, staticmethod) or isinstance(func, classmethod):
        # ��һ���ຯ���������������װ����������
        real_func = func.__func__
    else:
        real_func = func
    
    def wrapped_func(*args, **kwargs):
        global exclist
        
        try:
            real_func(*args, **kwargs)
        except AssertionError, e:
            # ��ExpectError ��װ AssertionError����������
            fmt_list = traceback.format_exception(ExpectError, ExpectError(e.message), sys.exc_info()[2])
            exclist.append("".join(fmt_list))
        except Exception:
            # �����쳣��ԭ������
            exclist.append(traceback.format_exc())
            
    # ������ຯ�������������������а�װ            
    if isinstance(func, staticmethod):
        return staticmethod(wrapped_func)
    elif isinstance(func, classmethod):
        return classmethod(wrapped_func)
    else:
        return wrapped_func
# ===== (end)expect ��� =======
            

def assert_equal(lhs, rhs, errmsg=None):
    '''
    @summary: ����lhs��rhs���
    @param errmsg: ����ʧ��ʱ��ʾ����Ϣ
    '''
    if errmsg is None:
        errmsg = "%s doesn't equal to: %s" % (lhs, rhs)
    
    if lhs != rhs:
        raise AssertionError, errmsg

expect_equal = wrap_expect(assert_equal)

def assert_not_equal(lhs, rhs, errmsg=None):
    '''
    @summary: ����lhs��rhs�����
    @param errmsg: ����ʧ��ʱ��ʾ����Ϣ
    '''
    if errmsg is None:
        errmsg = "%s equals to: %s" % (lhs, rhs)
        
    if lhs == rhs:
        raise AssertionError, errmsg

expect_not_equal = wrap_expect(assert_not_equal)

def assert_true(expr, msg=None):
    '''
    Fail the test unless the expression is true.
    '''
    if not expr: raise AssertionError,msg
        
expect_true = wrap_expect(assert_true)
        
def assert_false(expr, msg=None):
    '''
    Fail the test if the expression is true.
    '''
    if expr: raise AssertionError, msg
    
expect_false = wrap_expect(assert_false)
                                
def assert_gt(lhs, rhs, errmsg=None):
    '''
    @summary: ����lhs����rhs
    @param errmsg: ����ʧ��ʱ��ʾ����Ϣ
    '''
    if errmsg is None:
        errmsg = "%s is less than or equal to %s" % (lhs, rhs)
    
    if lhs <= rhs:
        raise AssertionError, errmsg

expect_gt = wrap_expect(assert_gt)

def assert_bound(value, lb, hb, errmsg=None):
    '''
    @summary: ����value����lb��hb֮�䣬�����߽�
    @param errmsg: ����ʧ��ʱ��ʾ����Ϣ
    @param lb: ����
    @param hb: ����
    '''
    if errmsg is None:
        errmsg = "%s is not in [%s, %s]" % (value, lb, hb)
    
    if value < lb or value > hb:
        raise AssertionError, errmsg

expect_bound = wrap_expect(assert_bound)

def assert_in_list(ele, lis, errmsg=None):
    '''
    @summary: ����element��list�е�һ��Ԫ��
    '''
    if errmsg is None:
        errmsg = "%s is not in %s" % (ele, lis)
    
    if ele not in lis:
        raise AssertionError, errmsg

expect_in_list = wrap_expect(assert_in_list)

def assert_process_started(processpath, *ports):
    '''
    @summary: ����C��������
    @param processpath: ���̵ľ���·��
    @param ports: ���̶˿ں��б�
    '''
    if not checker.check_process_started(processpath, *ports):
        ports_str = ",".join([str(p) for p in ports])
        raise AssertionError, "Process is not started: %s [%s]" % (processpath, ports_str)

expect_process_started = wrap_expect(assert_process_started)



def assert_process_not_started(processpath, *ports):
    '''
    @summary: ����C����δ����
    @param processpath: ���̵ľ���·��
    @param ports: ���̶˿ں��б�
    '''
    if checker.check_process_started(processpath, *ports):
        ports_str = ",".join([str(p) for p in ports])
        raise AssertionError, "Process is started: %s [%s]" % (processpath, ports_str)

expect_process_not_started = wrap_expect(assert_process_not_started)

def assert_file_equal(file1, file2, errmsg=None):
    '''
    @summary: ���������ļ�һ�£�ͨ��md5ֵ�������ж�
    @param errmsg : ����ʧ��ʱ��ʾ����Ϣ
    '''
    if errmsg is None:
        errmsg = "%s doesn't equal to: %s" % (file1, file2)
    print file1
    print file2
    
    m1 = commands.getoutput("md5sum %s| awk '{print $1}'"%file1)
    m2 = commands.getoutput("md5sum %s| awk '{print $1}'"%file2)
    if m1  != m2 :
         raise AssertionError, errmsg


expect_file_equal = wrap_expect(assert_file_equal)

def assert_path_not_contain(dirpath, filename, r=False):
    '''
    @summary: ����·���в������ļ�
    @param filename: ���Ժ�����չ����*, ?
    @param r: �Ƿ�ݹ���ҡ�Ĭ��False
    '''
    if checker.check_path_contain(dirpath, filename, r):
        raise AssertionError, "File '%s' in path: %s" % (filename, dirpath)

expect_path_not_contain = wrap_expect(assert_path_not_contain)    

def assert_path_contain(dirpath, filename, r=False):
    '''
    @summary: ����·���в������ļ�
    @param filename: ���Ժ�����չ����*, ?
    @param r: �Ƿ�ݹ���ҡ�Ĭ��False
    '''
    if checker.check_path_contain(dirpath, filename, r) == False:
        raise AssertionError, "File '%s' is not in path: %s" % (filename, dirpath)

expect_path_not_contain = wrap_expect(assert_path_contain)    

def assert_log_not_contain(log_reader, regex, ignore_list=[]):
    '''
    @summary: ������־�в����������ַ���
    @param log_reader: LogReader����
    @param regex: �����ַ���
    @param ignore_list: ���Է���ignore regex����
    '''
    if checker.check_log_contain(log_reader, regex, ignore_list):
        raise AssertionError, "Regex '%s' in log '%s' from pos %d" % (regex, log_reader.logpath, log_reader.pos)

expect_log_not_contain = wrap_expect(assert_log_not_contain)    


def assert_log_contain(log_reader, regex, ignore_list=[]):
    '''
    @summary: ������־�в����������ַ���
    @param log_reader: LogReader����
    @param regex: �����ַ���
    @param ignore_list: ���Է���ignore regex����
    '''
    if checker.check_log_contain(log_reader, regex, ignore_list) == False:
        raise AssertionError, "Regex '%s' in log '%s' from pos %d" % (regex, log_reader.logpath, log_reader.pos)  

expect_log_not_contain = wrap_expect(assert_log_contain)

def assert_raise(*exc_cls_args):
    '''@summary: ���Ժ����׳�ָ�����͵��쳣
    @attention: ����װ����������ֱ�ӵ���
    @param exc_cls_args: Exception Classes'''
    def do_assert_raise(func):
        
        def wrapped_func(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except exc_cls_args:
                # ������Ԥ�ڵ��쳣
                pass
            except Exception:
                # �����������쳣��ֱ�������׳�
                raise
            else:
                # û�з����쳣
                raise AssertionError, "Assert Raise Failed: Except %s, Actual NO Raise" % str(exc_cls_args)
        
        return wrapped_func
    return do_assert_raise


def _test_assert_raise():
    class Exc1(Exception):
        pass
    
    class Exc2(Exception):
        pass
    
    class Exc3(Exception):
        pass
    
    @assert_raise(Exc1, Exc2)
    def func1(a, b):
        raise Exc1
    
    @assert_raise(Exc1, Exc2)
    def func2(a, b):
        raise Exc2
    
    @assert_raise(Exc1, Exc2)
    def func3(a, b):
        pass
    
    @assert_raise(Exc1, Exc2)
    def func4(a, b):
        raise Exc3, "Not in expect exception list"
    
    try:
        func1(1, 2)
    except Exception:
        raise
    else:
        print "func1 ok"    # expect

    try:
        func2(1, 2)
    except Exception:
        raise
    else:
        print "func2 ok"    # expect
            
    try:
        func3(1, 2)
    except Exception, e:
        print "func3(no exception):", type(e), e   # expect
    else:
        print "func3 ok"
        
    try:
        func4(1, 2)
    except Exception, e:
        print "func4(other exception):", type(e), e   # expect
    else:
        print "func4 ok"

def _test_expect():
    print "before expect:", str_exclist()
    expect_equal(1, 1)
    print "expect succeeded:", str_exclist()
    expect_equal(1, 2)
    print "expect failed:", str_exclist()
    clear_exclist()
    print "clear exclist:", str_exclist()
    
def _test_class_expect():
    class T(object):
        def obj_assert_5(self, key):
            if key != 5:
                raise Exception, "Object Assert"
        obj_expect_5 = wrap_expect(obj_assert_5)
        
        @staticmethod
        def static_assert_5(key):
            if key != 5:
                raise Exception, "Static Assert"
        static_expect_5 = wrap_expect(static_assert_5)
        
        @classmethod
        def class_assert_5(cls, key):
            if key != 5:
                raise Exception, "Class Assert"
        class_expect_5 = wrap_expect(class_assert_5)
              
    t = T()
    t.obj_expect_5(5)
    print "object expect true:", str_exclist()
    t.obj_expect_5(6)
    print "object expect failed:", str_exclist()
    
    T.static_expect_5(5)
    print "static expect true:", str_exclist()
    T.static_expect_5(6)
    print "static expect failed:", str_exclist()
    
    T.class_expect_5(5)
    print "class expect true:", str_exclist()
    T.class_expect_5(6)
    print "class expect failed:", str_exclist()
    
    clear_exclist()

if __name__ == "__main__":
    print "===== _test_assert_raise() ====="
    _test_assert_raise()
    
    print
    print "===== _test_expect() ====="
    _test_expect()
    
    print
    print "===== _test_class_expect() ====="
    _test_class_expect()

