# -*- coding: gb2312 -*- 

'''
US 协议相关的模块-US2DA
@authors  :   U{jinjingting<mailto: jinjingting>}
@copyright:   
@date     :   2009-08-17
@version  :   1.0.0.0
'''

from frame.lib.commonlib.apicom.exception import AssertException
from frame.lib.commonlib import checker


# @note: 所有函数中的msg和log_suc参数都已废弃

def AssertTrue(val, msg="", log_suc=True):
    if not val:
        raise AssertException, "Assert True Failed"
    

def AssertFalse(val, msg="", log_suc=True):
    if val:
        raise AssertException, "Assert False Failed"
    

def AssertEqual(lhs, rhs, msg="", log_suc=True):
    if lhs != rhs:
        raise AssertException, "Assert '%s Equals %s' Failed" % (lhs, rhs)


def AssertNotEqual(lhs, rhs, msg="", log_suc=True):
    if lhs == rhs:
        raise AssertException, "Assert NOT Equals Failed. Both are %s" % lhs
    

def AssertRound(expect, actual, range, msg="", log_suc=True):
    diff = abs(expect - actual)
    
    if diff > range:
        raise AssertException, "Assert Round Failed. Expect %s, Actual %s" % (expect, actual)
    
    
def AssertIn(item, aggregate, msg="", log_suc=True):
    if item not in aggregate:
        raise AssertException, "Assert Item In Failed: %s" % str(item)
    
def AssertNotIn(item, aggregate, msg="", log_suc=True):
    if item in aggregate:
        raise AssertException, "Assert Item NotIn Failed: %s" % str(item)

def AssertLessThan(lhs, rhs, msg="", log_suc=True):
    if lhs >= rhs:
        raise AssertException, "Assert '%s Less Than %s' Failed" % (lhs, rhs)
    

def AssertGreaterThan(lhs, rhs, msg="", log_suc=True):
    if lhs <= rhs:
        raise AssertException, "Assert '%s Greater Than %s' Failed" % (lhs, rhs)


def AssertProcExist(procname, msg="", log_suc=True):
    if not checker.check_process_exist(procname):
        raise AssertException, "Assert Process Exist Failed: %s" % procname
    
    
def AssertPortExist(port, msg="", log_suc=True):
    if not checker.check_port_exist(port):
        raise AssertException, "Assert Port Exist Failed: %s" % port
    

def AssertLogContains(log_reader, regex, msg="", log_suc=True):
    "@param log_reader: LogReader对象"
    if not checker.check_log_contains(log_reader, regex):
        raise AssertException, "Assert Log Contains Failed: '%s'" % regex


def AssertLogNotContain(log_reader, regex, ignore_list=[], msg="", log_suc=True):
    "@param log_reader: LogReader对象"
    if checker.check_log_contains(log_reader, regex, ignore_list):
        raise AssertException, "Assert Log NOT Contain Failed: '%s'" % regex
    
    
def AssertPathNotContain(dirpath, filename, r=False, msg="", log_suc=True):
    '''
    @param filename: 可以含有扩展符号*, ?
    @param r: 是否递归查找。默认False
    '''
    if checker.check_path_contains(dirpath, filename, r):
        raise AssertException, "Assert Path NOT Contain Failed: %s" % filename
    

def AssertRaise(*exc_cls_args):
    '''
    @note: 函数装饰器。不能进行普通的调用
    @param exc_cls_args: Exception Class Tuples
    '''
    
    except_cls_t = exc_cls_args
    
    def do_AssertRaise(func):
        function = func
        def wrapped_func(*args, **kwargs):
            try:
                function(*args, **kwargs)
            except except_cls_t:
                # 发生了预期的异常
                pass
            except Exception, e:
                # 发生了其他异常
                raise AssertException, "Assert Raise Failed. Except %s, Actual %s" % (str(except_cls_t), e.__class__)
            else:
                # 没有发生异常
                raise AssertException, "Assert Raise Failed: Except %s, Actual NO Raise" % str(except_cls_t)
        return wrapped_func
    
    return do_AssertRaise
    

def test():
    "单元测试"
    AssertEqual(1, 1)
    AssertNotEqual(1, 1)
    AssertIn(3, (4,3), "Check 3 in (4,3)")
    AssertLessThan(2.1,2.3)
    AssertLessThan(2.4,2.3)
    AssertGreaterThan(2.4,2.5)


def test_assert_raise():
    class Exc1(Exception):
        pass
    
    class Exc2(Exception):
        pass
    
    class Exc3(Exception):
        pass
    
    @AssertRaise(Exc1, Exc2)
    def func1(a, b):
        raise Exc1
    
    @AssertRaise(Exc1, Exc2)
    def func2(a, b):
        raise Exc2
    
    @AssertRaise(Exc1, Exc2)
    def func3(a, b):
        pass
    
    @AssertRaise(Exc1, Exc2)
    def func4(a, b):
        raise Exc3
    
    func1(1, 2)
    func2(1, 2)
    func3(1, 2)
    func4(1, 2)
    
    
if __name__ == "__main__":
    test()
    test_assert_raise()
    
