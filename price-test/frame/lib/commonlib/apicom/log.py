# -*- coding: gb2312 -*- 

'''
日志模块
@authors  :   U{xieping<mailto: xieping>}
@copyright:   
@date     :   2009-09-08
@version  :   1.0.0.0
'''

import logging;
import os;
import re;
import share;

curLogger = None;

def getLogger(fn):
    logger = logging.Logger('funcLog');
    hdlr = logging.FileHandler(fn)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(funcName)s %(lineno)d %(message)s');
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.NOTSET)
    logging.raiseExceptions = 0;

    return logger,hdlr;

#return logger for decorator
def getDecoLogger(fn):
    logger = logging.Logger('methodLog');
    hdlr = logging.FileHandler(fn)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s');
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.NOTSET)
    logging.raiseExceptions = 0;
    
    return logger,hdlr;


def __getLogInfo__(msg):
    global curLogger;
    try:
        import   traceback;
        lineNo = traceback.extract_stack()[-3][1];
        funcName = traceback.extract_stack()[-3][2];
        fileName = traceback.extract_stack()[-3][0];
        fileName = os.path.basename(fileName);
        
        import inspect;
        curFuncName = inspect.currentframe().f_back.f_code.co_name;

        curLogger = share.logger;
        if curLogger != None:
            s = """curLogger.""" + curFuncName + """('''""" + fileName + """ """ + funcName + """ """ + str(lineNo) + """ """ + msg + """'''); """;
            c = compile(s,'','exec')
            return c;
        else:
            return '';
    except Exception,e:
        return '';

def debug(msg):
    try:
        exec __getLogInfo__(msg);
    except:
        pass;

def info(msg):
    try:
        exec __getLogInfo__(msg);
    except Exception,e:
        pass;


def warn(msg):
    try:
        exec __getLogInfo__(msg);
    except:
        pass;


def error(msg):
    try:
        exec __getLogInfo__(msg);
    except Exception,e:
        pass;


     
    
