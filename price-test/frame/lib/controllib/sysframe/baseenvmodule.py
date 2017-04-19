# -*- coding: GB18030 -*-
"""
@author: songyang
@modify: guoan
@modify: maqi
@modify: geshijing
@date: Nov 29, 2011
@summary: ���𻷾����ͳһ����
@version: 1.1.0.1
@copyright: Copyright (c) 2011 XX, Inc. All Rights Reserved
"""

from frame.lib.deploylib.basemodule import BaseModule


class BaseEnvModule(BaseModule):
    def __init__(self,host="127.0.0.1", user="localuser", local_path="./",instance_name=None,passwd=None,**args):
        """
        @note: host, user, local_path����init֮ǰ����ֵ��self.host_info��dict���ˣ�����Ҫ��init�и�ֵ
        """
        #ÿ���඼��һ��type���ԣ�������Զ�Ӧ����ʵ��keyֵ
        self.type = None
        #������Կ���wget����ʧ�ܵ�ʱ�����Լ���
        self.retry_num = 3
        #���ñ�ģ���ж��ٵĶ˿�
        self.port_num = 0
        self.listen_port = None
        self.port_list = []
        #�������ξ���ģ��ʵ��,��ʾһ��������� ��ģ��ע�������ʵ����ʵ������ģ�
        self.module_rel_set = []
        #ÿ��ģ�����Χģ�����,��ʾ��ģ�� ����һ���ж���ģ��
        self.all_rel_module = []
        #����ĳЩģ����Ҫ������ʱ�򣬿���ͨ��instance_name��������
        self.instance_name = instance_name
        #log�������ڸ���ģ��дlog
        self.log = None
        #����linuxϵͳ�����handler
        self.sys = None
        #ÿ��ģ�����������Ĭ�Ϻ���bin conf data,֧����չ�����Ե����ļ�������
        self.element_dict = {}
        #����element���صı���
        self.element_list = []
        #ģ������Դ���ֵ�
        self.src_dict={}
        #ģ������Դ��ԭ��Ϣ����
        self.src_list=[]

        #���ڼ�¼�����ϸ��Ϣ����dashboardչʾ
        self.result_obj = None
        #���ڶ˿�����Ӧ
        self.portalloc = None
        self.port_segs = []


    def init_handlers(self,log):
        #ʲô�������������ȡelement�����Ϣ
        return 0

    def load_remote_module(self, rel_path):
        """
        @author:liqiuhua
        @note: ͨ��module load��Ӧ��client lib
        @param rel_path:�����client path��lib·��
        """
        client_path = os.path.join(os.path.expanduser('~'),self.host_info["client_path"])
        abs_path = client_path+"/"+rel_path
        mname,ext = os.path.splitext(os.path.basename(abs_path))
        fp,pathname,desc = imp.find_module(mname,[os.path.dirname(abs_path)])
        sys.path.append(os.path.dirname(abs_path))
        try:
            m = imp.load_module(mname,fp,pathname,desc)
        finally:
            if fp:
                fp.close()
        return m

    def append_sys_path(self, sys_path):
        sys.path.append(sys_path)
