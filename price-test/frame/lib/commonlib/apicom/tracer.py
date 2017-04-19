# -*- coding: gb2312 -*-

import os
import re
import sys
import linecache
import traceback

import share;


def getExceptionStack():
    e_type, e_value, e_tb = sys.exc_info()
    msgList = traceback.extract_tb(e_tb)
    msg = '';
    for filename, lineno, name, line in msgList:
        if line != None and not re.search('raise',line):
            m1 = '[' + os.path.basename(str(filename)) + ':' + str(lineno) + '] ';
            msg += m1.ljust(22) + str(name).ljust(25) + ' -->  ' + str(line) + '\n';

    eStrType = str(e_type);
    m0 = re.match("<(type|class) '([^)]*)'>",str(e_type));
    if m0:
        eStrType = m0.group(2);
                    
    preList = str(e_value).split('\n');
    m = re.match('^[ \t]*([a-zA-Z0-9\.]*(Exception|Error)): ',preList[-1]);
    if not m: 
        preList[-1] = eStrType + ': ' + preList[-1];

    msg += '\n'.join(preList); 

    return msg;

def getExceptionStr():
    e_type, e_value, e_tb = sys.exc_info();
    preList = str(e_value).split('\n');
    
    eStrType = str(e_type);
    m0 = re.match("<(type|class) '([^)]*)'>",str(e_type));
    if m0:
        eStrType = m0.group(2); 

    m = re.match('^[ \t]*([a-zA-Z0-9\.]*(Exception|Error)): ',preList[-1]);
    if not m:
        msg = eStrType + ': ' + preList[-1];
    else:
        msg = preList[-1];

    return msg;

def traceLine(frame, event, arg):
    if event == "line":
        lineno = frame.f_lineno
        filename = frame.f_globals["__file__"]
        if (filename.endswith(".pyc") or
            filename.endswith(".pyo")):
            filename = filename[:-1]
        name = frame.f_globals["__name__"]
        line = linecache.getline(filename, lineno);
        output = "%s:%s: %s" %(filename, lineno, line.rstrip());
        if share.traceFlag == True:
            share.traceLogger.info(output);
    return traceLine

def traceFunc(frame, event, arg):
    if event == "call":
        filename = frame.f_globals["__file__"]
        if (filename.endswith(".pyc") or
            filename.endswith(".pyo")):
            filename = filename[:-1]
        s = filename + ':' + str(frame.f_lineno) + ' ' + frame.f_back.f_code.co_name + '-->' + frame.f_code.co_name;
        t = '(';
        for i in range(0,frame.f_code.co_argcount):
             if i > 0:
                 t += ',';
             t = t + frame.f_code.co_varnames[i];

        t += ')';
        if share.traceFlag == True:
            share.traceLogger.info(s+t);        

traceModeDict = {'line':traceLine,'func':traceFunc};


if __name__ == "__main__":
    def g(a):
        print 1;
        print a;
        pass;
    def f(a):
        g(a);

    f(1);
