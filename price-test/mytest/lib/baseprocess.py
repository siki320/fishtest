# -*- coding: GB18030 -*-

'''
Created on 2011-8-15

@author: tongdangdang
'''
import sys
import os  
import time  
import signal 
import traceback  
import subprocess
from frame.lib.commonlib.dlog import dlog
from frame.lib.commonlib import autosleep
from frame.lib.commonlib import asserts

__all__ = ["subwork", "trace_back", "os", "time", "traceback", "subprocess", "signal"]  

def trace_back():  
    try:  
        type, value, tb = sys.exc_info()  
        return str(''.join(traceback.format_exception(type, value, tb)))  
    except:  
        return ''  
def getCurpath():  
    try:  
        return os.path.normpath(os.path.join(os.getcwd(),os.path.dirname(__file__)))  
    except:  
        return  
class Subwork:  
    """add timeout support! 
    if timeout, we SIGTERM to child process, and not to cause zombie process safe! 
    """  
    def __init__(self, cmd=None, stdin=None, stdout=None, stderr=None, cwd='.', timeout=5*60*60):  
        """default None 
        """  
        self.cmd       = cmd  
        self.Popen     = None  
        self.pid       = None  
        self.returncode= None  
        self.stdin     = None  
        self.stdout    = stdout  
        self.stderr    = stderr  
        self.cwd       = cwd  
        self.timeout   = int(timeout)  
        self.start_time= None  
        self.msg       = ''  
    def send_signal(self, sig):  
        """Send a signal to the process 
        """  
        os.kill(self.pid, sig)  
          
    def terminate(self):  
        """Terminate the process with SIGTERM 
        """  
        self.send_signal(signal.SIGTERM)  
         
    def kill(self):  
        """Kill the process with SIGKILL 
        """  
        self.send_signal(signal.SIGKILL)  
     
    def wait(self):  
        """ wait child exit signal, 
        """  
        self.Popen.wait()  
    def free_child(self):  
        """ 
        kill process by pid 
        """  
        try:  
            self.terminate()
            self.wait()  
        except:  
            pass  
     
    def run_sync(self, is_output=False,is_shell=False):
        """
        run cmd sync,命令执行同步接口，等待执行完成返回
        如果is_outpu=True,self.stdout, self.stderr输出命令执行结果
        如果is_shell=True, 支持shell命令
        """
        try:
            print self.cmd,self.cwd
            self.Popen=subprocess.Popen(args=split_cmd(self.cmd),shell=is_shell,cwd=self.cwd)
            #self.Popen=subprocess.Popen(args=split_cmd(self.cmd),shell=is_shell,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=self.cwd)
            self.pid = self.Popen.pid
            dlog.info( "run_sync")
            if is_output:
                self.stdout, self.stderr=self.Popen.communicate()
                self.returncode = self.Popen.returncode
            else:
                self.returncode = self.Popen.wait()
            asserts.assert_equal(self.returncode, 0, "run_sync failed!")
        except:
  #          asserts.assert_equal(1,0,"###################")
            self.msg += trace_back()
            dlog.error( "run_sync except!"+self.msg)
            self.returncode = -9998

    def run(self):  
        """ 
        run cmd 
        """  
        print "[subwork]%s" % split_cmd(self.cmd)    
        try:  
            self.Popen = subprocess.Popen(args=split_cmd(self.cmd), stdout=self.stdout, stderr=self.stderr, cwd=self.cwd)  
            self.pid   = self.Popen.pid  
            self.start_time = time.time()   
            #time.sleep(7)   
            dlog.info( "running... %s, %s, %s" % (self.Popen.poll(), time.time() - self.start_time, self.timeout)  )
        except:  
            self.msg += trace_back()  
            self.returncode = -9998    
            dlog.info( "[subwork]!!error in Popen")
            
    def stop(self):  
        # check returncode 
        if self.Popen == None or self.Popen.poll() == None: # child is not exit yet!  
            self.free_child()   
            self.returncode = -9999  
        else:  
            self.returncode = self.Popen.poll() 
        code = True   
        return {"code":code, \
                "msg":self.msg, \
                "req":{"returncode":self.returncode}, \
                }
       

def sleeptill_haslog(logreader, regstr, maxwait=10):
    '''
    @summary: 等待log中出现某个正则
    @param logreader: LogReader对象
    @param regstr: 正则字符串
    @param maxwait: 最长等待时间，单位秒
    @raise AutosleepException: 超过最长等待时候
    '''
    autosleep.sleeptill_haslog(logreader, regstr, maxwait)

def sleeptill_hasprocess(processpath, maxwait=10):
    '''
    @summary: 等待C进程存在
    @param processpath: 进程的绝对路径
    @param maxwait: 最长等待时间，单位秒
    @raise AutosleepException: 超过最长等待时候
    '''
    autosleep.sleeptill_hasprocess(processpath, maxwait)
 
def sleeptill_noprocess(processpath, maxwait=10):
    '''
    @summary: 等待C进程不存在
    @param processpath: 进程的绝对路径
    @param maxwait: 最长等待时间，单位秒
    @raise AutosleepException: 超过最长等待时候
    '''
    autosleep.sleeptill_noprocess(processpath, maxwait)


def sleeptill_hasport(port, maxwait=10):
    '''
    @summary: 等待端口被占用
    @param port: 端口号
    @param maxwait: 最长等待时间，单位秒
    @raise AutosleepException: 超过最长等待时候
    '''
    autosleep.sleeptill_hasport(port, maxwait)

def sleeptill_noport(port, maxwait=10):
    '''
    @summary: 等待端口被释放
    @param port: 端口号
    @param maxwait: 最长等待时间，单位秒
    @raise AutosleepException: 超过最长等待时候
    '''
    autosleep.sleeptill_noport(port, maxwait)

def sleeptill_startprocess(processpath, port, maxwait=10):
     '''@param port: 可以是一个int，也可以是一个int list'''
     autosleep.sleeptill_startprocess(processpath, port, maxwait)

def sleeptill_killprocess(processpath, port, maxwait=10):
    '''@param port: 可以是一个int，也可以是一个int list'''
    autosleep.sleeptill_killprocess(processpath, port, maxwait)

     
def split_cmd(s):  
    """ 
    str --> [], for subprocess.Popen() 
    """  
    SC = '"'  
    a  = s.split(' ')  
    cl = []  
    i = 0  
    while i < len(a) :  
        if a[i] == '' :  
            i += 1  
            continue  
        if a[i][0] == SC :  
            n = i  
            loop = True  
            while loop:  
                if a[i] == '' :  
                    i += 1  
                    continue  
                if a[i][-1] == SC :  
                    loop = False  
                    m = i  
                i += 1  
            #print a[n:m+1]  
            #print ' '.join(a[n:m+1])[1:-1]  
            cl.append((' '.join(a[n:m+1]))[1:-1])  
        else:  
            cl.append(a[i])  
            i += 1  
    return cl  
def check_zero(dic=None):  
    """ 
    check returncode is zero 
    """  
    if not isinstance(dic, dict):  
        raise TypeError, "dist must be a Distribution instance"  
    print "returncode :", int(dic["req"]["returncode"])  
    if int(dic["req"]["returncode"]) == 0:  
        return True, dic["msg"]  
    else:  
        return False, dic["msg"]  
    
def get_pid(process):
    import commands
    pids = []
    cmd = "ps aux | grep -v grep |grep  '%s' " % process
    dlog.info(cmd)
    info = commands.getoutput(cmd)
    infos = info.split('\n')
    if infos[0] == '':
        return pids
    if len(infos) >0:
        pids = []
        for info in infos:
            pids.append(info.split()[1])
        return pids
    else:
        return pids
    
def kill_process(process):
    pids = get_pid(process)
    for pid in pids:
        try:
            os.kill(int(pid),signal.SIGKILL)
        except:
            pass
        #while pid in get_pid(process):
            #time.sleep(5)
            #sleeptill_noprocess(self.binpath)
  
#---------------------------------------------  
# main-test  
#---------------------------------------------  
if __name__ == '__main__' :   
    curlCMDS = './a.out'  
    #print shell_2_tty(_cmd=cmds, _cwd=None, _timeout=10)
    kill_process('./a.out')
    sw = Subwork(cmd = curlCMDS,cwd='/home/work/tools/BQ_TEST_LIB/') 
    sw.run()
    time.sleep(2)
    sw.stop()
    print "\nexit!"
    time.sleep(10)    
