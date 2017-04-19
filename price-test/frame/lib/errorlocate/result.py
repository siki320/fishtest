# -*- coding: GB18030 -*-
'''
Created on May 20, 2012

@author: caiyifeng<caiyifeng>
'''

from frame.lib.errorlocate.action import RuleMatch
from frame.lib.errorlocate.mail import mail_html

class ErrlocateResult(object):
    '''@summary: keyinfo result'''
    def __init__(self):
        self.case_failed_info = []  # keyinfo����
        self.ra = RuleMatch([])

    def add_failed_info(self, keyinfo):
        self.case_failed_info.append(keyinfo)

    def err_auto_locating(self):
        '''@summary: �������ռ�keyinfo��Ϣ, �Դ�������Զ���λ'''
        # û�д���, ֱ�ӷ���
        if len(self.case_failed_info) == 0:
            return
        
        self.ra = RuleMatch(self.case_failed_info)
        self.ra.print_err_info()
        
    def gen_mail_report(self, mailpath):
        mail = mail_html()
        mail.gen_mail_report(self.ra, mailpath)

    def __add__(self, other):
        self.ra += other.ra
        return self
