# -*- coding: GBK -*-
"""
    @author     : yuanyi03
    @date       : Mon 18 Mar 2013 11:36:41 PM CST
    @last update: Mon 18 Mar 2013 11:36:41 PM CST
    @summary    : 
    @version    : 1.0.0.0
"""

import sys,os,getopt
import imp,inspect

from frame.lib.commonlib.dlog import *
from frame.lib.controllib.sysframe.caseplug.sys_case import Sys_Case

class SysCasePicker(object):

    def __init__(self):
        self.suites={}
        self.ENVFILE_PREFIX="case"
        self.ENVFILE_SUFFIX=".topo"
        self.minInheritLen = len(inspect.getmro(Sys_Case))+1

    def __getsuite__(self,key):
        """
            get right suite object by key
        """
        suiteClassName =  key+"Suite"
        return self.suite_factory.getNewSuiteInstance(suiteClassName)

    def addcase(self,case):
        """
            insert case into suitable suite
            note: how to find the suitable suite?
                In the case's hierarchy, the first class which inherit Sys_Case directly
        """
        if case.__class__.__name__ == "Sys_Case":
            suite = self.__getsuite__("Sys")
            if suite == None:
                dlog.warning("I can't find suitable suite object for case [%s] ignore"%(case.__class__.__name__))
                return False
            suite.addcase(case)
            return True
        hierachy = inspect.getmro(case.__class__)
        if len(hierachy) < self.minInheritLen:
            dlog.warning("the case hierachy should at least inherit Sys_Case: %s ignore"%(case.__class__.__name__))
            return False
            
        # case <-> suite  name format should be XXX_case.py 
        suiteClass = hierachy[1].__name__
        if len(suiteClass.split('_')) < 2 :
            dlog.warning("the basic case name format err: %s"%(suiteClass))
            return False
        
        suite = self.__getsuite__(suiteClass.split('_')[0])    
        if suite == None:
            dlog.warning("I can't find suitable suite object for case [%s] ignore"%(case.__class__.__name__))
            return False
        suite.addcase(case)
        return True
        


    def __instantiate_class__(self,module):
        """
            instantiate the module 
            @return case object if instantiate suc, or None
        """
        caseclass = None
        for item in module.__dict__.keys():
               if inspect.isclass(module.__dict__[item]) and \
                       issubclass(module.__dict__[item],Sys_Case) and\
                       module.__dict__[item].__dict__['__module__'] == module.__name__:
                   caseclass = module.__dict__[item]
                   break
        if caseclass == None :
            dlog.warning("find module failed")
            return None
        try : 
            case = caseclass()
        except Exception:
            dlog.warning("instantiate case failed")
            return None

        return case

    def __load_module__(self,abspath,modulename):
        """
            load one case at path, the path should be XXXX.py
            @return case module if load suc, or None 
        """
        try:
            sys.path.append(os.path.dirname(abspath))
            fp,pathname,desc = imp.find_module(modulename,\
                    [os.path.dirname(abspath)])
            module = imp.load_module(modulename, fp, pathname, desc)
        except Exception,e:
            dlog.warning("case %s:%s load failed."%(abspath, modulename), exc_info=True)
            dlog.warning("%s",str(e))
            return None
        finally:
            fp.close()
        return module
        
    def getSuites(self):
        """
            return suites.
        """
        return self.suites

    def __getallpath__(self, paths):
        topickPaths = []
        # add all case path to topickPaths list
        for path in paths:
            path = os.path.abspath(path)
            if not os.path.exists(path):
                dlog.warning("path: %s is not exists."%(path))
                continue
            if os.path.isdir(path):
                for i in os.listdir(path):
                    topickPaths.append(os.path.join(path,i))
                continue
            if os.path.isfile(path) and path not in topickPaths: 
                topickPaths.append(path)
        for ind in topickPaths :
            if os.path.isfile(ind):
                continue
            for i in os.listdir(ind):
                #bug
                topickPaths.append(os.path.join(ind,i))
            
        return topickPaths

    def __caseValid__(self,abspath,filename):
        # __init__.py ignore
        modulename, ext = os.path.splitext(filename)
        if modulename == "__init__":
            #dlog.debug("case: %s ignoral by init file"%(path))
            return False
        if ext != ".py" :
            #dlog.debug("case: %s ignoral by file format err"%(path))
            return False
        return True


    def pickcases(self, args, suite_factory, result):
        """
            pick case from the paths
        """
        # get all path
        self.suite_factory = suite_factory

        topickPaths = self.__getallpath__(args)
        if len(topickPaths) == 0:
            dlog.info("no case need to load")
            return False

        for path in topickPaths:
            filename = os.path.basename(path)
            abspath = os.path.abspath(path) 
            modulename, ext = os.path.splitext(filename)

            # case valid check
            if not self.__caseValid__(abspath,filename):
                #dlog.warning("case :%s not valid"%(filename))
                continue
            
            casemodule = self.__load_module__(abspath,modulename)
            if casemodule == None : 
                # instantiate a basic object only for status record
                case = Sys_Case()
                case.set_status(Sys_Case.STATS.LOAD_FAILED)
                case.set_desc(case.__doc__)
                case.set_filepath(abspath)
            else:
                case = self.__instantiate_class__(casemodule)
                if case == None:
                    case = Sys_Case()
                    # INSTANCE_FAILED
                    case.set_status(Sys_Case.STATS.INSTANCE_FAILED)
                else:
                    # check env conf is exists
                    envfile = os.path.dirname(abspath)+"/" + self.ENVFILE_PREFIX+self.ENVFILE_SUFFIX
                    if not os.path.exists(envfile):
                        # ENVCONF_MISS
                        case.set_status(Sys_Case.STATS.ENVCONF_MISS)
                    else:
                        case.set_status(Sys_Case.STATS.READY)
                        case.set_envconf(envfile)

                case.set_desc(case.__doc__)
                case.set_filepath(abspath)
            if not self.addcase(case):
                dlog.warning("suite which case used not exists.%s "%(modulename))
        pass


def TEST_getallpath():
    t = SysCasePicker()
    tx = t.__getallpath__("./suiteplug")
    print tx

def usage():
    print "Usage: SysCasePicker.py [options] ..."

def main():
    try:
        opts,args = getopt.getopt(sys.argv[1:],"vh",["version","help"])
    except GetoptError:
        sys.exit(2)

    TEST_getallpath()

if __name__ == "__main__":
    main()
    pass
