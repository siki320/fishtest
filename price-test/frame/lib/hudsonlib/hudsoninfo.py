# -*- coding: GB18030 -*-   
# 提取hudson信息,共分为三类:
# 1. 触发信息, 返回类型为TriggerInfo对象
# 2. scm pooling info. 返回类型为list(ChangeLog)对象
# 3. 监控路径的revision信息. 返回类型为string
# 需要提供的参数为job_name和build_number, 在hudson上可由环境变量JOB_NAME和BUILD_NUMBER获得
# @author : tangyuanyuan

from frame.lib.commonlib.dtssystem2 import dtssystem
from frame.lib.commonlib.dlog import dlog

import os
import string
import re
from xml.dom.minidom import parseString

class HudsonJob():
    def __init__(self, job_name, build_number):
        self.job_name = job_name
        self.build_number = build_number

    def __str__(self):
        return "%s %s" % (self.job_name, self.build_number)

class TriggerInfo():
    def __init__(self):
        #1. 上游触发的任务列表. 为HudsonJob类型的list
        self.trigger_upstream_jobs = []
        #2. 是否由timer触发
        self.trigger_by_timer = False
        #3. 是否由svn change触发
        self.trigger_by_scm = False
        #4. 是否由用户由"立即构建"触发
        self.trigger_users = []

    def __str__(self):
        ret_str = "Triggered by:"
        if len(self.trigger_upstream_jobs) == 0 and \
                len(self.trigger_users) == 0 and \
                not self.trigger_by_timer and \
                not self.trigger_by_scm:
            return ret_str + "Undetermined"

        if len(self.trigger_upstream_jobs) > 0:
            ret_str += " upstream job " + ','.join([str(upjob) for upjob in self.trigger_upstream_jobs])
        if len(self.trigger_users) > 0:
            ret_str += " user " + ','.join(self.trigger_users)
        if self.trigger_by_scm:
            ret_str += " scm change"
        if self.trigger_by_timer:
            ret_str += " timer"
        return ret_str

class ChangeLog():
    def __init__(self, author, changelist, msg):
        #ci 作者
        self.author = author
        #更改的文件列表
        self.changelist = changelist
        #作者ci时的信息
        self.msg = msg

    def __str__(self):
        ret_str = ""
        ret_str += "author: %s" % self.author
        ret_str += "changelist: %s" % self.changelist
        ret_str += "msg: %s" % self.msg
        return ret_str
        
class hudson_info_retriever():
    def retrieve_trigger_info(self, job_name, build_number):
        trigger_info = TriggerInfo()
        
        try:
            build_xml = self._get_build_xml(job_name, build_number)
        except:
            return None

        #1. trigger by upstream
        re_upstream = re.compile('(?<=build number <a href=")[^"]+(?=")')
        upstream_url_list = re_upstream.findall(build_xml)
        for upstream_url in upstream_url_list:
            tokens = upstream_url.strip('/').split('/')
            upstream_job = tokens[-2]
            upstream_build = tokens[-1]
            trigger_info.trigger_upstream_jobs.append(HudsonJob(upstream_job, upstream_build))

        #2. trigger by user
        re_user = re.compile('(?<=启动用户<a href=")[^"]+(?=")')
        user_list = re_user.findall(build_xml)
        for user in user_list:
            tokens = user.strip('/').split('/')
            user_name = tokens[-1]
            trigger_info.trigger_users.append(user_name)

        #3. trigger by timer
        re_timer = re.compile('Started by timer')
        if re_timer.search(build_xml) != None:
            trigger_info.trigger_by_timer = True

        #4. trigger by scm
        re_scm = re.compile('Started by an SCM change')
        if re_scm.search(build_xml) != None:
            trigger_info.trigger_by_scm = True

        dlog.info("Trigger info: %s" % str(trigger_info))
        return trigger_info

    def retrieve_change_log(self, job_name, build_number):
        svn_change_list = []

        try:
            changelist_txt = self._get_change_list(job_name, build_number)
        except:
            return None
        doc = parseString(changelist_txt)
        entry_list = doc.getElementsByTagName('logentry')
  
        for entry in entry_list:
            author_list = entry.getElementsByTagName('author')
            if len(author_list) != 1:
                raise Exception("changelog.xml out of format")
            author = author_list[0].childNodes[0].nodeValue
            
            msg_list = entry.getElementsByTagName('msg')
            msg = msg_list[0].childNodes[0].nodeValue
            
            change_list = entry.getElementsByTagName('path')
            svn_change_list_txt = []
            for change in change_list:
                action = change.getAttribute('action')
                path = change.childNodes[0].nodeValue
                svn_change_list_txt.append('%s  %s' % (action, path))
                
            svn_change_list.append(ChangeLog(author, '\n'.join(svn_change_list_txt), msg))
        dlog.info("Changelog: %s" % '\n'.join(['%s'% s for s in svn_change_list]))
        return svn_change_list

    def retrieve_revision(self, job_name, build_number):
        try:
            return self._get_revision(job_name, build_number)
        except:
            dlog.warning("Failed to get revision info")
            return None

    def _get_ftp_file(self, job_name, build_number, filename):
        filepath = self._hudson_ftp_dir(job_name, build_number) + '/%s' % filename
        local_path = os.path.join(os.path.dirname(__file__), '../../log/.%s' % filename)
        dtssystem("rm -rf %s" % local_path)
        cmd = "wget %s -O %s" % (filepath, local_path)
        ret = dtssystem(cmd)
        if ret != 0:
            dlog.warning("execute cmd [%s] failed" % cmd)
            raise Exception("fail to get %s from hudson master [%s]" % (filename, cmd))
        return file(local_path).read()
 
    def _get_http_file(self, job_name, build_number):
        local_path = '.http.tmp'
        local_gbk_path = local_path + '.gbk'
        cmd = "wget --http-user=vitual_nova --http-password=9bf130320e5b2103c1764934d0254c68 %s -O %s" % (self._hudson_page(job_name, build_number), local_path)
        ret = dtssystem(cmd)
        if ret != 0:
            raise Exception("fail to get hudson http page [%s]" % cmd)

        ret = dtssystem("iconv -f utf-8 -t gb18030 -o %s %s" % (local_gbk_path, local_path))
        if ret != 0:
            raise Exception("fail to convert hudson page from utf-8 to gb18030")
        return file(local_gbk_path).read()

    def _get_change_list(self, job_name, build_number):
        return self._get_ftp_file(job_name, build_number, 'changelog.xml')

    def _get_build_xml(self, job_name, build_number):
        return self._get_http_file(job_name, build_number)
        
    def _get_revision(self, job_name, build_number):
        return self._get_ftp_file(job_name, build_number, 'revision.txt')

    def _hudson_ftp_dir(self, job_name, build_number):
        hudson_url = os.environ['HUDSON_URL']
        hudson_url=hudson_url.replace('http://', '')
        hudson_master = hudson_url.split('/')[0].split(':')[0]
        return "ftp://%s/CI/hudson/jobs/%s/builds/%s" % (hudson_master, job_name, build_number)
    
    def _hudson_page(self, job_name, build_number):
        return "%s/job/%s/%s" % (os.environ['HUDSON_URL'], job_name, build_number)


if __name__ == "__main__":
#following is test
#测试时需设置环境变量HUDSON_URL,在hudson上运行时,该环境变量由hudson export, 无需用户设置
    os.environ['HUDSON_URL'] = 'http://'
    hr = hudson_info_retriever()
    aa = hr.retrieve_trigger_info('', '1015') #upstream
    print aa
    if len(aa.trigger_upstream_jobs) != 0:
        print "***************"
        info = aa.trigger_upstream_jobs[0]
        print aa.trigger_upstream_jobs[0].job_name
        print aa.trigger_upstream_jobs[0].build_number
        
    print hr.retrieve_trigger_info('dp-slow', '926') # trigger by user
    #print hr.retrieve_trigger_info('ctr-nts', '2997') # trigger by scm
    #print hr.retrieve_trigger_info('ctr-nts', '3000') # by timer

    #print ["%s\n" % str(changelog) for changelog in hr.retrieve_change_log('ctr-quick', '2037')]

    #print hr.retrieve_revision('ctr-quick', '2037')
