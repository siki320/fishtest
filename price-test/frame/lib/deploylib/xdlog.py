# -*- coding: GB18030 -*-
'''
Created on Api 18, 2012

@author: maqi
'''

import logging
from frame.lib.commonlib.dlog import _dlog, dlog, update_nest_level

class XDLog(_dlog):
    """
    @note: ��װԶ��log�࣬����һ�����Ļ�log���󣬽�Զ�̵ĵ�����Ϣ����Զ��log�����ӡ
           ͬʱ����Զ��ģ�����ڻ�����Ҳ��ӡһ��ģ���������־
           ע�⣺����־����������commonlib��dlog����
    """
    def __init__(self, center_log=dlog, logger_name="xdlog", module_name=""):
        super(XDLog, self).__init__(logger_name, module_name)

        self.center_log = center_log
        self.module_name = module_name

    def __getstate__(self):
        odict = self.__dict__.copy()
        del odict["logger"]
        del odict["center_log"]
        return odict

    def __setstate__(self,state):
        self.__dict__.update(state)
        self.center_log = dlog
        self.logger = logging.getLogger(self.logger_name)
        
        # �����ܵ�logger level
        self.logger.setLevel(logging.DEBUG)

        # �����ļ���־
        self.init_logger(self.logpath)

    def debug(self, msg, *args, **kwargs):
        update_nest_level(kwargs)
        super(XDLog,self).debug(msg, *args, **kwargs)
        self.center_log.debug(msg, *args, tag_name=self.tag_name, **kwargs)

    def info(self, msg, *args, **kwargs):
        update_nest_level(kwargs)
        super(XDLog,self).info(msg, *args, **kwargs)
        self.center_log.info(msg, *args, tag_name=self.tag_name, **kwargs)

    def warning(self, msg, *args, **kwargs):
        update_nest_level(kwargs)
        super(XDLog,self).warning(msg, *args, **kwargs)
        self.center_log.warning(msg, *args, tag_name=self.tag_name, **kwargs)

    def error(self, msg, *args, **kwargs):
        update_nest_level(kwargs)
        super(XDLog,self).error(msg, *args, **kwargs)
        self.center_log.error(msg, *args, tag_name=self.tag_name, **kwargs)

    def critical(self, msg, *args, **kwargs):
        update_nest_level(kwargs)
        super(XDLog,self).critical(msg, *args, **kwargs)
        self.center_log.critical(msg, *args, tag_name=self.tag_name, **kwargs)
        
