# -*- coding: GB18030 -*- 
import os
import time
import socket
from frame.lib.commonlib.dtssystem2 import dtssystem,dtssystem_out
from frame.lib.commonlib.dlog import dlog
import pickle

running_ccover=False

class CovInfo():
    def __init__(self):
        self.case_cov_rel={}
        self.cov_case_rel={}
        self.fun_map={}
        self.src_map={}

    def __add__(self, other):
        self.do_merge(other, 'case_cov_rel')
        self.do_merge(other, 'cov_case_rel')
        self.fun_map = dict(self.fun_map, **other.fun_map)
        self.src_map = dict(self.src_map, **other.src_map)
        return self

    def do_merge(self, other, dictname):
        dict1 = getattr(self, dictname)
        dict2 = getattr(other, dictname)
        key1 = dict1.keys()
        key2 = dict2.keys()
        common_keys = set(key1) & set(key2)
        sep_key2 = set(key2) - common_keys
        
        for key in common_keys:
            dict1[key].extend(dict2[key])

        for key in sep_key2:
            dict1[key] = dict2[key]

        return self

covinfo = CovInfo()

def get_covfile_save_path():
    covfile_save_path = os.path.join(os.path.dirname(__file__), '../../../log/ccover')
    if not os.path.exists(covfile_save_path):
        os.makedirs(covfile_save_path)

    return covfile_save_path

def get_init_covfile_path():
    init_covfile_dir=get_covfile_save_path()
    init_covfile_path=os.path.join(init_covfile_dir, 'test.cov.init')
    if init_covfile_path == os.environ['COVFILE']:
        init_covfile_path += '.1'
    return init_covfile_path 
    
def backup_cov_init():
    dtssystem("cp %s %s" % (os.environ['COVFILE'], get_init_covfile_path()))

def init():
    global running_ccover
    if os.environ.has_key('COVFILE') and os.path.exists(os.environ['COVFILE']):
        running_ccover=True
        backup_cov_init()
        ret = dtssystem('cov01 -1')
        if ret != 0:
            dlog.warning("failed to true on ccover")
            return False
        return True
    else:
        dlog.warning("environment variable 'COVFILE' not exists or corresponding COVFILE not exists. unable to run ccover mode")
        return False
    
def restore_init_covfile():
    dtssystem("cp %s %s" % (get_init_covfile_path(), os.environ['COVFILE']))

def save_covinfo(casename):
    '''
    get the case covered fun/code file info
    '''
    if not running_ccover:
        return
    #only get what covered. the awk is used to filtered those not covered
    #$2 of awk is the function name. $3 is the source code filename
    cmd = "covfn -f %s -r --html -k %s | grep '1 / 1' | awk -F '<td>' '{printf(\"%%s\\t%%s\\n\",$2,$3)}' | grep -v '^$' " % \
            (os.environ['COVFILE'], os.path.relpath(os.path.dirname(os.environ['COVFILE']), os.path.curdir))
    ret, stdout, stderr = dtssystem_out(cmd)

    if ret != 0:
        dlog.warning("failed to get covinfo of case %s" % casename)
        return
    
    global covinfo
    covinfo.case_cov_rel[casename] = []

    for line in stdout.strip('\n').split('\n'):
        try:
            fun, src = line.split('\t')
            hash_fun=hash(fun)
            hash_src=hash(src)
            covinfo.fun_map[hash_fun] = fun
            covinfo.src_map[hash_src] = os.path.relpath(src, os.path.relpath(os.path.dirname(os.environ['COVFILE'])))

            key = (hash_fun, hash_src)
            covinfo.case_cov_rel[casename].append(key)
            if not covinfo.cov_case_rel.has_key(key):
                covinfo.cov_case_rel[key] = []
            covinfo.cov_case_rel[key].append(casename)
        except:
            dlog.debug('failed to parse line: %s' % line)
        
    #restore_init_covfile()

def finalize(result):
    '''
    save it to dtestresult to make it easy to be merged
    '''
    if not running_ccover:
        return
    
    global covinfo
    result.covinfo = covinfo

def upload_covinfo(cov=None):
    global covinfo
    if cov:
        upload_cov=cov
    else:
        if not running_ccover:
            return
        upload_cov=covinfo

    pickle_file='cov.tmp.pickle'
    pickle.dump(upload_cov, open(pickle_file,'wb'))
    if os.environ.has_key('JOB_NAME'):
        dest_name=os.environ['JOB_NAME']+'.cov.pickle.' + str(int(time.time()))
    else:
        dest_name=socket.gethostname() + '_' + os.environ['USER'] + '.cov.pickle.' + str(int(time.time()))

    tmp_name=dest_name + '.tmp'
    
    sshpass_tool=os.path.join(os.path.dirname(__file__), '../deploylib/sshpass')
    HOST="yx-testing-ecom6242.yx01"
    USER="nts"
    HOME="/home/nts/covinfo"
    PASSWD="CAPHI2008"
    
    if not os.path.exists(sshpass_tool):
        dlog.warning("%s does not exist" % sshpass_tool)
        return
    
    cmd="%s -p %s scp %s %s@%s:%s/%s" % \
            (sshpass_tool, \
            PASSWD, \
            pickle_file, \
            USER, \
            HOST, \
            HOME, \
            tmp_name)
    ret=dtssystem(cmd)
    if ret != 0:
        dlog.warning("failed to upload covinfo")
        return

    cmd='%s -p %s ssh %s@%s "mv %s/%s %s/%s"' % \
            (sshpass_tool,\
            PASSWD, \
            USER, \
            HOST, \
            HOME, \
            tmp_name, \
            HOME, \
            dest_name )
    ret=dtssystem(cmd)
    if ret != 0:
        dlog.warning("failed to move covinfo")
        return

    dlog.info("successfully to upload covinfo [%s] "% dest_name)
 
