# -*- coding: GB18030 -*-
'''
Created on May 20, 2012

@author: caiyifeng<caiyifeng>
'''

from frame.lib.commonlib.dlog import dlog
from frame.lib.errorlocate import baserules
from frame.lib.errorlocate.baserules import errInstance

class RuleMatch(object):
    def __init__(self, _list = None):
        self.keyinfo_list = _list
        self.start_err_flag = False     # ȫ�ּ�¼�Ƿ���fail������start�׶�
        self.test_err_flag = False      # ͬ�ϣ�test�׶�
        self.reason_idx = 1
        self.noHitErr = None
        self.noHitKeyInfo = []
        
        if self.keyinfo_list is not None:
            # ���ɵ�ǰ����ģ��Ķ�λ����
            self.makeRules(self.keyinfo_list)
            self.analyse()
            self.make_result_dict()

    def doRuleMatch(self):
        if self.keyinfo_list != []:
            # ���ɵ�ǰ����ģ��Ķ�λ����
            self.makeRules(self.keyinfo_list)
            self.analyse()
            self.make_result_dict()

    def __add__(self, other):
        if other != None:
            if self.keyinfo_list == None:
                self.keyinfo_list = []
            if other.keyinfo_list == None:
                other.keyinfo_list = []
            self.keyinfo_list.extend(other.keyinfo_list)
        return self

    def makeRules(self, std_keyinfo_list):
        # ���ع�������
        self.start_rules = [baserules.RULE_cfg_missing(), 
                            baserules.RULE_file_missing(), 
                            baserules.RULE_dir_empty(),
                            baserules.RULE_no_such_directory()
                            ]
        self.test_rules = [baserules.RULE_assert_failed()]
        
        # �������й���
        rule_loaded = [] # ��¼�����Ѿ����ص�ģ��
        for std_keyinfo in std_keyinfo_list:
            if str(std_keyinfo.__class__) in rule_loaded: # �Ѽ���������
                continue
            
            rule_module = std_keyinfo.rulemodule
            if not rule_module:
                # û��ģ���Ӧ��rules������
                continue
            
            for aclass in dir(rule_module):
                if 'RULE_' in aclass :
                    rule_class = getattr(rule_module, aclass)
                    stage = rule_class.rule_stage
                    
                    if stage == 'START' :
                        self.start_rules.append(rule_class())
                    elif stage == 'TEST' :
                        self.test_rules.append(rule_class())
                    else:
                        self.start_rules.append(rule_class())
                        self.test_rules.append(rule_class())
#                        raise Exception, "Unknown rule stage: %s" % stage
                        
            rule_loaded.append(str(std_keyinfo.__class__)) # ��¼

    def analyse(self):
        _list = self.keyinfo_list
        if len(_list) == 0:
            return
        
        for keyinfo in _list:
            # ���������쳣ʱ, ƥ����������
            start_ret = False
            test_ret = False
            if keyinfo.startException != "": 
                for rule in self.start_rules:
                    try:
                        if rule.module_match(keyinfo) and rule.match(keyinfo):
                            self.start_err_flag = True
                            start_ret = True
                    except Exception:
                        dlog.error("Start rule match error: %s\n%s", 
                                     type(rule), 
                                     "".join( [c+"\n" for c in keyinfo.get_casename_list()] ), 
                                     exc_info=True)
                if start_ret :
                    continue # ������һ��keyinfo
            
            # ���в����쳣ʱ, ƥ����Թ���
            if keyinfo.testException != "":
                for rule in self.test_rules:
                    try:
                        if rule.module_match(keyinfo) and rule.match(keyinfo):
                            self.test_err_flag = True
                            test_ret = True
                    except Exception:
                        dlog.error("Test rule match error: %s\n%s", 
                                     type(rule), 
                                     "".join( [c+"\n" for c in keyinfo.get_casename_list()] ), 
                                     exc_info=True)
            
            # �洢start��test��û�����е�keyinfo
            if not (test_ret or start_ret):
                self.noHitKeyInfo.append(keyinfo)
        
        # ��¼δ����keyinfo��case ��  module
        nohit_casenames = []
        nohit_module = set()
        for keyinfo in self.noHitKeyInfo:
            nohit_casenames.extend(keyinfo.get_casename_list())
            nohit_module.add(keyinfo.module)
            
        # ���й����δ���е����
        if self.noHitKeyInfo:
            self.noHitErr = errInstance("unknown", "Unknown(All rules missed)")
            self.noHitErr.failed_case_list = nohit_casenames
            self.noHitErr.module = ','.join(nohit_module)

    def make_result_dict(self):
        # ������result.result_dict�ṹ���£�        
        #    {
        #        'Person1': 
        #            {
        #                'Module11': 
        #                    {
        #                        'Reason115': ['Case5', 'Case13'], 
        #                        'Reason111': ['Case1', 'Case9']
        #                    }, 
        #                'Module13': 
        #                    {
        #                        'Reason133': ['Case3', 'Case11'], 
        #                        'Reason137': ['Case7', 'Case15']
        #                    }
        #            }, 
        #        'Person0': 
        #            {
        #                ...
        #            }
        #    }
        self.result_dict = {}
        self.raw_owner = set()      # ������raw�ı������ڽ����ʼ��ռ���
        for rule in self.start_rules + self.test_rules:
            if not hasattr(rule, 'errlist'):
                continue
            
            for e in rule.errlist:
                self.raw_owner.add(e.responsible_person)
                    
                person_dict = self.result_dict.setdefault(e.responsible_person, {})
                module_dict = person_dict.setdefault(e.module, {})
                module_dict.setdefault(e.reason, []).extend(e.failed_case_list)
                
        # δ����ʱ
        if self.noHitKeyInfo:
            self.raw_owner.add(self.noHitErr.responsible_person)
            
            person_dict = self.result_dict.setdefault(self.noHitErr.responsible_person, {})
            module_dict = person_dict.setdefault(self.noHitErr.module, {})
            module_dict.setdefault(self.noHitErr.reason, []).extend(self.noHitErr.failed_case_list )
            
    def print_err_info(self):
        '''@summary: ��־��ӡ��λ���'''
        self.lines = ['']
        self.lines.append('='*10 + '  Start_Error_Auto_Locating_Info  ' + '='*10)
                
        if self.start_err_flag:
            self.lines.append('***** Failed information when module Starting *****')
            for rule in self.start_rules:
                self.print_info(rule)
            self.lines.append("")
                
        if self.test_err_flag:
            self.lines.append('***** Failed information when case being tested *****')
            for rule in self.test_rules:
                self.print_info(rule)
            self.lines.append("")
        
        # �����δ����
        if self.noHitKeyInfo:
            self.lines.append('***** All Rules missed, Failed information as below *****')
            self.lines.append("Person Responsible : %s"%self.noHitErr.responsible_person)
            self.lines.append("All Modules : %s"% self.noHitErr.module)
            self.lines.append('Failed Reason : %s'% self.noHitErr.reason)
            self.lines.append("Failed Cases : \n\t%s"%'\n\t'.join(self.noHitErr.failed_case_list))
            
        lastline = '='*10 + '   End_Error_Auto_Locating_Info   ' + '='*10
        dlog.diagnose("\n".join(self.lines).rstrip()+"\n"+lastline)

    def print_info(self, rule):
        _dict = {}
        for e in rule.errlist:
            _dict.setdefault((e.reason, e.responsible_person, e.module), []).extend(e.failed_case_list)
            
        for (reason, person, module), v1 in _dict.items():
            self.lines.append("Person Responsible : %s"%person)
            self.lines.append("Module : %s"%module)
            self.lines.append("Failed Reason %s : %s"%(self.reason_idx, reason))
            self.lines.append("Failed Cases : \n\t%s"%'\n\t'.join(v1))
            self.lines.append("")
            self.reason_idx += 1
            
