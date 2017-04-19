# -*- coding: GB18030 -*-
"""
@author: maqi
@date: Feb 2, 2011
@summary: dts deploy 异常类
@version: 1.0.0.0
@copyright: Copyright (c) 2011 XX, Inc. All Rights Reserved
"""

class XDError(Exception):
    '''base class for dts deploy exceptions'''
   
    pass
    
class XDFrameError(XDError):
    '''base class for framework exceptions'''
    
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg
    
    def __repr__(self):
        return 'Framework Error : ' + self.msg
    
class XDDeployError(XDError):
    '''base class for build exceptions'''

    err_collection = 0
    
    def __init__(self, msg, error_num):
        self.msg = msg
        XDDeployError.add_err_collection(error_num)
    
    def __str__(self):
        return self.msg
    
    def __repr__(self):
        return 'Deploy Error : ' + self.msg
    
    @classmethod
    def add_err_collection(self,err_num):
        XDDeployError.err_collection |= err_num 
    
    @classmethod
    def set_err_collection(self,err_num):
        XDDeployError.err_collection = err_num
    
    @classmethod
    def reset_err_collection(self):
        XDDeployError.err_collection = 0

class XDComponentError(XDFrameError):
    '''component exception'''
    
    def __repr__(self):
        return 'Component Error : ' + self.msg

class XDCommonError(XDDeployError):
    '''common exception'''

    def __init__(self, msg):
        super(XDCommonError,self).__init__(msg,128)
    
    def __repr__(self):
        return 'Common Error : ' + self.msg

class XDDownloadError(XDDeployError):
    '''download exception'''
    
    def __init__(self, msg):
        super(XDDownloadError,self).__init__(msg,64)
    
    def __repr__(self):
        return 'Download Error : ' + self.msg

class XDFileNotExistError(XDDeployError):
    '''file not exist exception'''
    
    def __init__(self, msg):
        super(XDFileNotExistError,self).__init__(msg,32)
    
    def __repr__(self):
        return 'File not exist Error : ' + self.msg
    
class XDDirNotExistError(XDDeployError):
    '''dir not exist exception'''
    
    def __init__(self, msg):
        super(XDDirNotExistError,self).__init__(msg,16)
    
    def __repr__(self):
        return 'Dir not exist Error : ' + self.msg
    
class XDNoModInfoError(XDDeployError):
    '''no mod info exception'''
    
    def __init__(self, msg):
        super(XDNoModInfoError,self).__init__(msg,8)
    
    def __repr__(self):
        return 'No mod info Error : ' + self.msg
    
class XDHadoopError(XDDeployError):
    '''hadoop exception'''
    
    def __init__(self, msg):
        super(XDHadoopError,self).__init__(msg,4)
    
    def __repr__(self):
        return 'Hadoop Error : ' + self.msg
    
class XDCommandError(XDDeployError):
    '''command exception'''
    
    def __init__(self, msg):
        super(XDCommandError,self).__init__(msg,2)
    
    def __repr__(self):
        return 'Command Error : ' + self.msg

def error_test():
    try:
        raise XDComponentError,'oops 1'
    except XDComponentError,e:
        print 'XD exception occurred, message:', e.msg

    try:
        raise XDCommonError,'oops 2'
    except XDCommonError,e:
        print 'XD exception occurred, message:', e.msg, 'error: ', e.err_collection
  
    try:
        raise XDDownloadError,'oops 3'
    except XDDownloadError,e:
        print 'XD exception occurred, message:', e.msg, 'error: ', e.err_collection

    try:
        raise XDFileNotExistError,'oops 4'
    except XDFileNotExistError,e:
        print 'XD exception occurred, message:', e.msg, 'error: ', e.err_collection

    try:
        raise XDDirNotExistError,'oops 5'
    except XDDirNotExistError,e:
        print 'XD exception occurred, message:', e.msg, 'error: ', e.err_collection

    try:
        raise XDNoModInfoError,'oops 6'
    except XDNoModInfoError,e:
        print 'XD exception occurred, message:', e.msg, 'error: ', e.err_collection
    
    try:
        raise XDHadoopError,'oops 7'
    except XDHadoopError,e:
        print 'XD exception occurred, message:', e.msg, 'error: ', e.err_collection
    
    try:
        raise XDCommandError,'oops 8'
    except XDCommandError,e:
        print 'XD exception occurred, message:', e.msg, 'error: ', e.err_collection
        XDDeployError.reset_err_collection()
    
    try:
        raise XDCommandError,'oops 9'
    except XDCommandError,e:
        print 'XD exception occurred, message:', e.msg, 'error: ', e.err_collection
        XDDeployError.set_err_collection(1)
        
    try:
        raise XDCommandError,'oops 10'
    except XDCommandError,e:
        print 'XD exception occurred, message:', e.msg, 'error: ', e.err_collection
    

if __name__ == '__main__':
    error_test()

