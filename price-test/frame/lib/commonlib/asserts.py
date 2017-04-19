# -*- coding: GB18030 -*-
'''
Created on Aug 30, 2011

@author: caiyifeng<caiyifeng>

@summary: 断言函数集合 ，包含assert & expect 
'''

import sys
import traceback
from frame.lib.commonlib import checker
#import hashlib
import commands


# ===== expect 相关 =======
# 全局变量，list of 异常堆栈字符串
exclist = []

def clear_exclist():
    '''@summary: 清空全局exclist'''
    global exclist
    del exclist[:]
    
def str_exclist():
    '''@summary: 将exclist文本化'''
    global exclist
    return "\n".join(exclist)
    
class ExpectError(AssertionError):
    '''包装 AssertionError，便于区分'''
    pass
    
def wrap_expect(func):
    '''@summary: expect包装函数，返回一个不抛出异常的断言函数
    @note: 异常被记录在全局的exclist中'''
    if isinstance(func, staticmethod) or isinstance(func, classmethod):
        # 是一个类函数，获得描述符包装的真正函数
        real_func = func.__func__
    else:
        real_func = func
    
    def wrapped_func(*args, **kwargs):
        global exclist
        
        try:
            real_func(*args, **kwargs)
        except AssertionError, e:
            # 用ExpectError 包装 AssertionError，便于区分
            fmt_list = traceback.format_exception(ExpectError, ExpectError(e.message), sys.exc_info()[2])
            exclist.append("".join(fmt_list))
        except Exception:
            # 其他异常，原样保留
            exclist.append(traceback.format_exc())
            
    # 如果是类函数，重新用描述符进行包装            
    if isinstance(func, staticmethod):
        return staticmethod(wrapped_func)
    elif isinstance(func, classmethod):
        return classmethod(wrapped_func)
    else:
        return wrapped_func
# ===== (end)expect 相关 =======
            

def assert_equal(lhs, rhs, errmsg=None):
    '''
    @summary: 断言lhs和rhs相等
    @param errmsg: 断言失败时显示的信息
    '''
    if errmsg is None:
        errmsg = "%s doesn't equal to: %s" % (lhs, rhs)
    
    if lhs != rhs:
        raise AssertionError, errmsg

expect_equal = wrap_expect(assert_equal)

def assert_not_equal(lhs, rhs, errmsg=None):
    '''
    @summary: 断言lhs和rhs不想等
    @param errmsg: 断言失败时显示的信息
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
    @summary: 断言lhs大于rhs
    @param errmsg: 断言失败时显示的信息
    '''
    if errmsg is None:
        errmsg = "%s is less than or equal to %s" % (lhs, rhs)
    
    if lhs <= rhs:
        raise AssertionError, errmsg

expect_gt = wrap_expect(assert_gt)

def assert_bound(value, lb, hb, errmsg=None):
    '''
    @summary: 断言value介于lb和hb之间，包含边界
    @param errmsg: 断言失败时显示的信息
    @param lb: 下限
    @param hb: 上限
    '''
    if errmsg is None:
        errmsg = "%s is not in [%s, %s]" % (value, lb, hb)
    
    if value < lb or value > hb:
        raise AssertionError, errmsg

expect_bound = wrap_expect(assert_bound)

def assert_in_list(ele, lis, errmsg=None):
    '''
    @summary: 断言element是list中的一个元素
    '''
    if errmsg is None:
        errmsg = "%s is not in %s" % (ele, lis)
    
    if ele not in lis:
        raise AssertionError, errmsg

expect_in_list = wrap_expect(assert_in_list)

def assert_process_started(processpath, *ports):
    '''
    @summary: 断言C进程启动
    @param processpath: 进程的绝对路径
    @param ports: 进程端口号列表
    '''
    if not checker.check_process_started(processpath, *ports):
        ports_str = ",".join([str(p) for p in ports])
        raise AssertionError, "Process is not started: %s [%s]" % (processpath, ports_str)

expect_process_started = wrap_expect(assert_process_started)



def assert_process_not_started(processpath, *ports):
    '''
    @summary: 断言C进程未启动
    @param processpath: 进程的绝对路径
    @param ports: 进程端口号列表
    '''
    if checker.check_process_started(processpath, *ports):
        ports_str = ",".join([str(p) for p in ports])
        raise AssertionError, "Process is started: %s [%s]" % (processpath, ports_str)

expect_process_not_started = wrap_expect(assert_process_not_started)

def assert_file_equal(file1, file2, errmsg=None):
    '''
    @summary: 断言两个文件一致，通过md5值来进行判断
    @param errmsg : 断言失败时显示的信息
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
    @summary: 断言路径中不含有文件
    @param filename: 可以含有扩展符号*, ?
    @param r: 是否递归查找。默认False
    '''
    if checker.check_path_contain(dirpath, filename, r):
        raise AssertionError, "File '%s' in path: %s" % (filename, dirpath)

expect_path_not_contain = wrap_expect(assert_path_not_contain)    

def assert_path_contain(dirpath, filename, r=False):
    '''
    @summary: 断言路径中不含有文件
    @param filename: 可以含有扩展符号*, ?
    @param r: 是否递归查找。默认False
    '''
    if checker.check_path_contain(dirpath, filename, r) == False:
        raise AssertionError, "File '%s' is not in path: %s" % (filename, dirpath)

expect_path_not_contain = wrap_expect(assert_path_contain)    

def assert_log_not_contain(log_reader, regex, ignore_list=[]):
    '''
    @summary: 断言日志中不含有正则字符串
    @param log_reader: LogReader对象
    @param regex: 正则字符串
    @param ignore_list: 忽略符合ignore regex的行
    '''
    if checker.check_log_contain(log_reader, regex, ignore_list):
        raise AssertionError, "Regex '%s' in log '%s' from pos %d" % (regex, log_reader.logpath, log_reader.pos)

expect_log_not_contain = wrap_expect(assert_log_not_contain)    


def assert_log_contain(log_reader, regex, ignore_list=[]):
    '''
    @summary: 断言日志中不含有正则字符串
    @param log_reader: LogReader对象
    @param regex: 正则字符串
    @param ignore_list: 忽略符合ignore regex的行
    '''
    if checker.check_log_contain(log_reader, regex, ignore_list) == False:
        raise AssertionError, "Regex '%s' in log '%s' from pos %d" % (regex, log_reader.logpath, log_reader.pos)  

expect_log_not_contain = wrap_expect(assert_log_contain)

def assert_raise(*exc_cls_args):
    '''@summary: 断言函数抛出指定类型的异常
    @attention: 函数装饰器，不能直接调用
    @param exc_cls_args: Exception Classes'''
    def do_assert_raise(func):
        
        def wrapped_func(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except exc_cls_args:
                # 发生了预期的异常
                pass
            except Exception:
                # 发生了其他异常，直接重新抛出
                raise
            else:
                # 没有发生异常
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

