# -*- coding: gb2312 -*- 

import os;
import sys;
import traceback;
import share;
import threading;
import log;
import tracer;
import socket;
#import netlib.netlib;
from exception import *;
import inspect

'''
revision@05/10/2010 by caihaipeng:
	add an extra control upon the behavior of decorator which is imposed upon either a class method or a factory
	function so that we can get a more concise description in the corresponding "test point" section of the WallE report

revision@05/11/2010 by caihaipeng:
	1.add a switch on the decoration feature itself, see the in-code annotation for more details
	2.add the "__realname__" attribute with the replaceMethodDecorator/replaceFuncDecorator so that the user could get
	  the real function name - the name of function to be decorated if necessary
'''

DECFLAGPREFIX = 'nodec'

def __genOutputFuncInfo(self,func,brief,arg1,arg2):
    outList = [];
    rpOutList = [];
    try:
        if(self != None):
            outList.append(self.__class__.__name__ + '.' + func.func_name);
            outList.append('(');
        else:
            outList.append(func.func_name);
            outList.append('(');
            
        rpOutList = outList[:];
        vars = func.func_code.co_varnames

        hasTupleFlag = False;
        if len(arg1) > 0:
            hasTupleFlag = True;
        for i in range(0,len(arg1)):
            if i > 0:
                outList.append(',');
                rpOutList.append(',');

            param = vars[i+1] + '=';
            rpParam = vars[i+1] + '=';
            if isinstance(arg1[i],int):
                param += str(arg1[i]);
                rpParam += str(arg1[i]);
            elif isinstance(arg1[i],str):
                anno = arg1[i]
                if brief and len(anno) >= 8:
				    anno = anno[:8]+"..."
                if len(anno) < 1:
                    anno = '""'
                param += '"' + anno + '"';
                rpParam +=  anno
            elif isinstance(arg1[i],socket.socket):
                param += '"socketObject:' + str(id(arg1[i])) + '"';
                rpParam +=  'socketObject:' + str(id(arg1[i]));                
            elif brief and (inspect.ismethod(arg1[i]) or inspect.isfunction(arg1[i])):
                funcname = arg1[i].__name__
                if funcname in ("replaceFuncDecorator", "replaceMethodDecorator"):
                    if hasattr(arg1[i],"__realname__"):
                        funcname = arg1[i].__realname__
                    if inspect.ismethod(arg1[i]):
                        funcname = arg1[i].im_self.__class__.__name__ + "." + funcname
                param += funcname
                rpParam += funcname
            else:
                anno = str(arg1[i])
                if brief and len(anno) >= 8:
                    anno = anno[:8]+"..."
                param += anno
                rpParam +=  anno
                
            outList.append(param);
            rpOutList.append(rpParam);

        count =0;
        for k,v in arg2.items():
            if count == 0:
                if hasTupleFlag:
                    outList.append(',');
                    rpOutList.append(',');
            else:
                outList.append(',');
                rpOutList.append(',');
            param = str(k) + '='
            rpParam = str(k) + '='
            if isinstance(v,int):
                param += str(v);
                rpParam += str(v);
            elif isinstance(v,str):
                anno = str(v)
                if brief and len(anno) >= 8:
                    anno = anno[:8]+"..."
                if len(anno) < 1:
                    anno = '""'   
                param += '"' + anno +'"';
                rpParam += anno;
            elif isinstance(v,socket.socket):
                param += '"socketObject:' + str(id(v)) + '"';
                rpParam +=  'socketObject:' + str(id(v));                   
            elif brief and (inspect.ismethod(v) or inspect.isfunction(v)):
                funcname = v.__name__
                if funcname in ("replaceFuncDecorator", "replaceMethodDecorator"):
                    if hasattr(v,"__realname__"):
                        funcname = v.__realname__
                    if inspect.ismethod(v):
                        funcname = v.im_self.__class__.__name__ + "." + funcname
                param += funcname
                rpParam += funcname
            else:    
                anno = str(v)
                if brief and len(anno) >= 8:
                    anno = anno[:8]+"..."
                param += anno
                rpParam +=  anno

            count += 1;
            outList.append(param);                        
            rpOutList.append(rpParam);                        
    except Exception,e:
        print '__genOutputFuncInfo Exception:',e;
        outList = [];
        outList.append(func.func_name +'(');
        rpOutList = [];
        rpOutList.append(func.func_name +'(');
    return outList,rpOutList;

def methodDecorator(needRp=True, brief=False):
    def newDecorator(func):
        def replaceMethodDecorator(self,*arg1,**arg2):
            # revision by caihp,  2010-05-11, the beginning 
            #
            # add an extra control by a specific attribute, named "nodec"$methodname, upon the decoration feature
            # for the purpose of flexibility in terms of using or dismissing this feature. There are actual
            # application-level needs, that we don't want the decorator to get the firsthand exception handling, say.
            # 
            flag = None
            attr = DECFLAGPREFIX + func.__name__
            try:
                flag = hasattr(self, attr)
                if flag:
                    flag = getattr(self, attr)
            except AttributeError:
                flag = False

            if flag:
                return func(self, *arg1, **arg2)
            # revision by caihp,  2010-05-11, the end 
            try:
                _logger = share.logger;
                _report = share.reporter;  
                _lock = share.rpLock;
                _debug = share.debug;
            except:
                _logger = None;
                _report = None;  
                _debug = 'DEBUG'

            succ = True;
            exp = None;
            try:
                return func(self,*arg1,**arg2);
            except Exception,e:      
                succ = False;
                exp = e;
            finally:
                outList,rpOutList = __genOutputFuncInfo(self,func,brief,arg1,arg2);
                if(succ):
                    outList.append(') OK.');
                    log.info(''.join(outList));

                    if(_report != None and needRp):
			_lock.acquire();
                        _report.step_begin(outList[0]);                    
                        _report.expect(''.join(rpOutList[2:]),'OK');                    
                        _report.actual(''.join(rpOutList[2:]),'OK');   
                        _report.step_end();
			_lock.release();
                else:
                    outList.append(') FAIL.Exception:');
                    outList.append(tracer.getExceptionStr());
                    log.error(''.join(outList));
                    log.error('\n'.join(['================Exception Stack begin==============',
                                                 tracer.getExceptionStack()]));
                    log.error('================Exception Stack end  ==============\n');
                                   
                    if(_report != None and needRp):
			_lock.acquire();
                        _report.step_begin(outList[0]);   
                        _report.expect(''.join(rpOutList[2:]),'OK');                    
                        _report.actual(''.join(rpOutList[2:]),'FAIL:%s' %(tracer.getExceptionStr(),));
                        _report.step_end();
			_lock.release();
#
#                    if isinstance(exp,netlib.netlib.SendException):
#                        print tracer.getExceptionStack();
#                        raise netlib.netlib.SendException,tracer.getExceptionStack();
#                    elif isinstance(exp,netlib.netlib.RecvException):
#                        print tracer.getExceptionStack();
#                        raise netlib.netlib.RecvException,tracer.getExceptionStack();
#                    else:
#                        raise CaseException,tracer.getExceptionStack();


        def simpleReplaceMethodDecorator(self,*arg1,**arg2):
             return func(self,*arg1,**arg2);

        replaceMethodDecorator.__realname__ = func.__name__
        return replaceMethodDecorator
    return newDecorator

def funcDecorator(needRp=True, brief=False):
    def newFuncDecoator(func):
        def replaceFuncDecorator(*arg1,**arg2):
            # revision by caihp,  2010-05-11, the beginning 
            #
            # add an extra control by a specific attribute, named "nodec", upon the decoration feature
            # for the purpose of flexibility in terms of using or dismissing this feature. There are actual
            # application-level needs, that we don't want the decorator to get the firsthand exception handling, say.
            # 
            flag = None
            attr = DECFLAGPREFIX
            try:
                flag = hasattr(func, attr)
                if flag:
                    flag = getattr(func, attr)
            except AttributeError:
                flag = False

            if flag:
                return func(*arg1, **arg2)
            # revision by caihp,  2010-05-11, the end 
            try:
                _logger = share.logger;
                _report = share.reporter; 
                _lock = share.rpLock;
                _debug = share.debug;
            except:
                _logger = None;
                _report = None;  
                _debug = 'DEBUG'  

            succ = True;
            exp = None;            
            expectExceptionFlag = False;
            try:
                return func(*arg1,**arg2);
            except ExpectException,e:
                expectExceptionFlag = True;
            except Exception,e:      
                succ = False;
                exp = e;                
            finally:
                outList,rpOutList = __genOutputFuncInfo(None,func,brief,arg1,arg2);

                if(succ):
                    outList.append(') OK.');
                    log.info(''.join(outList));                
                    if(_report != None and needRp):
                        _lock.acquire();
                        _report.step_begin(outList[0]);                    
                        _report.expect(''.join(rpOutList[2:]),'OK');                    
                        _report.actual(''.join(rpOutList[2:]),'OK');
                        _report.step_end();
                        _lock.release();
                else:
                    outList.append(') FAIL.Exception:');
                    outList.append(tracer.getExceptionStr());
                    log.error(''.join(outList));
                    log.error('\n'.join(['================Exception Stack begin==============',
                                                 tracer.getExceptionStack()]));
                    log.error('================Exception Stack end  ==============\n');
                                   
                    if(_report != None and needRp):
                        _lock.acquire();
                        _report.step_begin(outList[0]);                    
                        _report.expect(''.join(rpOutList[2:]),'OK');                    
                        _report.actual(''.join(rpOutList[2:]),'FAIL:%s' %(tracer.getExceptionStr(),));
                        _report.step_end();
                        _lock.release();
#
#                    if isinstance(exp,netlib.netlib.SendException):
#                        print tracer.getExceptionStack();
#                        raise netlib.netlib.SendException,tracer.getExceptionStack();
#                    elif isinstance(exp,netlib.netlib.RecvException):
#                        print tracer.getExceptionStack();
#                        raise netlib.netlib.RecvException,tracer.getExceptionStack();
#                    elif not expectExceptionFlag:
#                        raise CaseException,tracer.getExceptionStack();                        

        def simpleReplaceFuncDecorator(*arg1,**arg2):
             return func(*arg1,**arg2);    
             
        replaceFuncDecorator.__realname__ = func.__name__
        return replaceFuncDecorator
    return newFuncDecoator


