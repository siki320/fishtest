# -*- coding: GB18030 -*-
"""
    @author     : yuanyi03
    @date       : Thu 21 Mar 2013 04:05:53 PM CST
    @last update: Thu 21 Mar 2013 04:05:53 PM CST
    @summary    : 
            suitefactory load all suite module in init process
            default path is current path + /frame/lib/controllib/sysframe/suiteplug/
    @version    : 1.0.0.0
"""

import sys,os,getopt,imp
import traceback

from frame.lib.commonlib.dtssystem import *
from frame.lib.controllib.sysframe.suiteplug.syssuite import *
from frame.lib.commonlib.dlog import *

class SysSuiteFactory(object):

    #default sys plug path
    SYS_PLUGIN_PATH=os.path.join(os.path.abspath(os.path.dirname(__file__)),"./suiteplug/")

    def __init__(self, plugin_path=None):
        self.plugin_path = plugin_path
        self.suites = {}
        self.load_plugin(self.SYS_PLUGIN_PATH)
        if self.plugin_path != None:
            self.load_plugin(self.plugin_path)

    def load_plugin(self, plugin_path):
        for plug_file in os.listdir(plugin_path):
            filename = os.path.basename(plug_file)
            modulename,ext = os.path.splitext(filename)
            if filename == __file__:
                continue
            if modulename == "__init__":
                continue
            if ext != ".py":
                continue
            module = self.__loadsuitemodule__(plugin_path+plug_file)
            if module == None:
                continue
            obj,cls = self.__instancemodule__(module)
            if cls == None or obj == None :
                continue
            self.suites[cls.__name__]=obj

    def __loadsuitemodule__(self,modulepath):
        """
            load suite module by modulepath 
        """
        filename = os.path.basename(modulepath)
        modulename,ext = os.path.splitext(filename)
        dlog.debug("begin to load %s"%(modulename))
        sys.path.append(os.path.dirname(modulepath)) 
        fp,pathname,desc = imp.find_module(modulename,[os.path.dirname(modulepath)])
        try: 
            module = imp.load_module(modulename,fp,pathname,desc)
            dlog.debug("module : %s load success"%(modulename))
        except Exception:
            dlog.error("Suite Load Failed: %s"%(modulepath), exc_info=True)
            return None
        finally:
            fp.close()
        return module

    def __instancemodule__(self,module):
        """
            instance module 
        """
        moduleclass = None
        if inspect.getmodule(SysSuite).__name__.split(".")[-1] \
                == module.__name__.split(".")[-1]: 
            return SysSuite(),SysSuite
        for item in module.__dict__.keys():
               if module.__dict__[item]==SysSuite:
                   continue
               if inspect.isclass(module.__dict__[item]) and \
                       issubclass(module.__dict__[item],SysSuite) :
                   moduleclass = module.__dict__[item]
                   break
        if moduleclass == None :
            #dlog.warning("find class failed,%s"%(module.__name__))
            return None,None
        try : 
            m = moduleclass()
        except Exception:
            dlog.warning("instantiate suite failed", exc_info=True)
            return None,moduleclass
        return m,moduleclass



    def getNewSuiteInstance(self,classname):
        """
            return a idl instance of suite named $modulename
        """
        if classname not in self.suites.keys():
            dlog.warning("Have no this suite(%s)"%(classname))
            return None
        return self.suites[classname]

    def run_suites(self, result, conf_file, deploy_mode, xstp_mode):
        for aname in self.suites.keys():
            self.suites[aname].set_conf_file(conf_file)
            self.suites[aname].set_deploymode(deploy_mode)
            self.suites[aname].set_xstpmode(xstp_mode)
            self.suites[aname].run_cases(result)

