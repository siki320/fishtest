# -*- coding: GB18030 -*- 
import os
import socket
import math
from frame.lib.commonlib.dtssystem2 import dtssystem,dtssystem_out
from frame.lib.commonlib.dlog import dlog
import glob
import re

svndiff=None
case_rel=[]#each element is a tuple, first is case list, second is valgrind id list
use_history_data=False

def get_valgrind_raw_data_path():
    '''
    valgrindÖ±½ÓÉú³ÉµÄ½á¹ûÎ»ÖÃ
    '''
    valgrind_data_path=os.path.join(os.path.dirname(__file__), '../../../log/valgrind')
    if not os.path.exists(valgrind_data_path):
        os.makedirs(valgrind_data_path)
    return valgrind_data_path

def get_valgrind_parsed_data_path():
    '''
    vgd-parser²ú³öÎ»ÖÃ
    '''
    valgrind_data_path=os.path.join(os.path.dirname(__file__), '../../../log/vgdout')
    return valgrind_data_path
    
def get_valgrind_tool_path():
    '''
    vgd-parser¹¤¾ßÎ»ÖÃ
    '''
    return os.path.join(os.path.dirname(__file__), '../../tools/valgrind/vgd-parser')

def is_running_valgrind():
    '''
    ÊÇ·ñÕýÔÚÒÔvalgrind·½Ê½ÔËÐÐ
    '''
    if os.environ.has_key('running_valgrind') and os.environ['running_valgrind'] == 'true':
        return True
    return False

def set_valgrind_running_mode(svn_diff_file="", use_history=False):
    '''
    ÔÚMainÒ»¿ªÊ¼, Èç¹ûÓÃ»§Ìí¼ÓÁËvalgrind²ÎÊý,ÄÇÃ´µ÷ÓÃ
    '''
    
    os.environ["running_valgrind"] = "true"

    if os.path.isfile(svn_diff_file):
        global svndiff
        svndiff = svn_diff_file
    
    valgrind_log_dir=get_valgrind_raw_data_path()
    parser_output_dir = get_valgrind_parsed_data_path()
    
    if os.path.exists(valgrind_log_dir):
        if not os.path.exists(valgrind_log_dir + '.bak'):
            dtssystem('mkdir -p %s.bak' % valgrind_log_dir)
        dtssystem('mv %s/* %s.bak/' % (valgrind_log_dir, valgrind_log_dir))
    else:
        dtssystem('mkdir -p %s' % valgrind_log_dir)

    if os.path.exists(parser_output_dir):
        if os.path.exists(parser_output_dir + '.last'):
            dtssystem('rm -rf %s.last' % parser_output_dir)
        dtssystem('mv %s %s.last' % (parser_output_dir, parser_output_dir))

    global valgrind_id
    global last_valgrind_id
    tmp='%s_%s' % (socket.gethostname(), os.path.abspath(__file__))
    valgrind_id=int(math.fabs(hash(tmp)))%10000
    last_valgrind_id=valgrind_id

    #process history
    global use_history_data
    use_history_data=use_history
    if use_history_data:
        download_history()
        
def get_job_name_build_number():
    if os.environ.has_key('JOB_NAME') and os.environ.has_key('BUILD_NUMBER'):
        job_name=os.environ['JOB_NAME']
        build_number=os.environ['BUILD_NUMBER']
    else:
        import datetime
        job_name=socket.gethostname() + '_' + os.environ['USER']
        build_number=datetime.datetime.now().strftime('%Y%m%d_%H%M')

    return job_name, build_number
    
def download_history():
    HISTORY_DOWN_TOOL = os.path.join(os.path.dirname(__file__), '../../hudsonbuild/valgrind/valgrind_downloader.sh')
    job_name, build_number = get_job_name_build_number()
    dest_dir = get_valgrind_parsed_data_path() + '.last'
    ret,stdout,stderr=dtssystem_out("sh -x %s %s %s %s" % (HISTORY_DOWN_TOOL, job_name, build_number, dest_dir))
    dlog.debug(stderr)
    if ret==0:
        dlog.info('Sucessfully download history of [%s:%s] to [%s]' % (job_name, build_number, dest_dir))
    else:
        dlog.warning('Failed to download history of [%s:%s] to [%s]' % (job_name, build_number, dest_dir))

def upload_history():
    HISTORY_UP_TOOL = os.path.join(os.path.dirname(__file__), '../../hudsonbuild/valgrind/valgrind_pusher.sh')
    
    job_name, build_number = get_job_name_build_number()
    vgdout = get_valgrind_parsed_data_path()
    raw=get_valgrind_raw_data_path()
    
    ret,stdout,stderr=dtssystem_out("sh -x %s %s %s %s %s" % (HISTORY_UP_TOOL, job_name, build_number, vgdout, raw))
    dlog.debug(stderr)
    if ret==0:
        dlog.info('Sucessfully uploaded history of [%s:%s]' % (job_name, build_number))
    else:
        dlog.warning('Failed to upload history of [%s:%s]' % (job_name, build_number))
    
def run_valgrind_parse_tool():
    '''
    ÔÚMain.py½áÊøÇ°µ÷ÓÃ
    '''
    
    valgrind_log_dir=get_valgrind_raw_data_path()
    parser_output_dir = get_valgrind_parsed_data_path()

    valgrind_tool = get_valgrind_tool_path()
    dtssystem('mkdir -p %s' % parser_output_dir)
    #-o ARG             : use ARG as out path [default "./out"]
    #-d ARG             : svn diff file path(include file name) [default null]
    #--old-path ARG     : last out path by vgd-parser [default null]
    #--in-path ARG      : valgrind log path, vgd-parser input path
    args = '--in-path %s -o %s ' % (valgrind_log_dir, parser_output_dir)
    if svndiff:
        args += '-d %s ' % svndiff
    if os.path.exists(parser_output_dir + '.last'):
        args += '--old-path %s ' % (parser_output_dir + '.last')
    cmd = '%s %s' % (valgrind_tool, args)
    dlog.debug('valgrind parser cmd:%s' % cmd)
    vgd_ret = dtssystem(cmd)
    if vgd_ret == 0:
        dlog.info('run vgd-parser success')
    else:
        dlog.warning('run vgd-parser fail')

    if use_history_data:
        upload_history()
 
def get_valgrind_cmd(cmd):
    '''
    ÒµÎñlibÖÐµ÷ÓÃ
    '''
    global valgrind_id
    if os.environ.has_key('running_valgrind') and os.environ['running_valgrind'] == 'true':
        bin_basename = os.path.basename(cmd.strip().split(' ')[0])
        valgrind_id += 1
        return "valgrind --tool=memcheck -v -q --track-origins=yes --leak-check=yes --malloc-fill=0x7 --free-fill=0x8 --log-file=%s/valgrind.%s.%d.$$ %s" % (get_valgrind_raw_data_path(), bin_basename, valgrind_id, cmd)
    else:
        return cmd

def record_case_rel(caselist):
    global last_valgrind_id
    global case_rel
    
    if last_valgrind_id == valgrind_id:
        return
    
    valgrind_id_list = []
    for i in range(last_valgrind_id+1, valgrind_id+1):
        valgrind_id_list.append(i)

    case_rel.append((caselist, valgrind_id_list))
    last_valgrind_id = valgrind_id

def print_case_rel(relation=None):
    if relation:
        case_rel_list=relation
    else:
        case_rel_list=case_rel

    log_lines=[]
    for case_list, valgrind_id_list in case_rel_list:
        for case in case_list:
            log_lines.append('%s\t\t\t%s' % (case, ','.join(['%d' % id for id in valgrind_id_list])))
    dlog.info('Valgrind report id & case relation: \nCase Name\t\t\t\t\tValgrind report id\n%s' % '\n'.join(log_lines))   

def merge_result():
    do_merge(get_valgrind_raw_data_path())
    for logdir in os.listdir(get_valgrind_parsed_data_path()):
        do_merge(os.path.join(get_valgrind_parsed_data_path(),logdir))

def do_merge(dir):
    module_dict={}
    
    all_files=glob.glob('%s/valgrind.*.[0-9]*.[0-9]*' % dir)
    for afile in all_files:
        filename=os.path.basename(afile)
        module=filename.split('.')[1]
        if module_dict.has_key(module):
            module_dict[module].append(afile)
        else:
            module_dict[module]=[afile]

    for module, files in module_dict.items():
        merged_file=os.path.join(dir, 'valgrind.%s.txt' % module)
        with open(merged_file, 'w') as f:
            for afile in files:
                f.write(file(afile).read())
                
if __name__ == "__main__":
    merge_result()
