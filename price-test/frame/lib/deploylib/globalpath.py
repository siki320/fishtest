# -*- coding: GB18030 -*-
"""
@author: guoan
@date: Nov 25, 2011
@summary: ��¼����ģ������Դ��·��
@version: 1.0.0.0
@copyright: Copyright (c) 2011 XX, Inc. All Rights Reserved
@modify: Ŀǰ���ģ�����;�Ѿ�����������rpyc_port���ڱ�ʹ��
"""

rpyc_port="60777"

class Base_global_info(object):
    """
    @note:������global_info�ļ������Ƕ���һ��dict��ʾ���������ģ�������������Ļ����̳д��࣬������
          ������safedownload.py��ǿ��صģ���ע���޸�
    """
    def __init__(self):
        #Ŀǰ��ʼ�����⼸��ֵ��Ϊ�˲�����Ҫ��ÿ������ط����ֵ���Ҫ��ʼ������
        self.global_dict = {}

    def get_global_dict(self):
        """
        @note:���global_dict
        """
        return self.global_dict

    def set_global_dict(self,path_dict):
        """
        @note:���ò�Ʒ��˽�еı����ֵ���Ϣ
        @param path_dict:˽�еı����ֵ���Ϣ
        """
        self.global_dict = path_dict
        return 0

    def has_key(self,key):
        """
        @note:ʵ���ֵ��has_key����
        @param key:����key
        @return :1 or 0
        """
        return self.global_dict.has_key(key)

    def get_global_dict_by_type(self, key):
        """
        @note:��ȡһ��ģ���Ӧ��dict
        @param key:����ģ���typeֵ
        @return :��ģ���Ӧ��dict�ʵ�,�����������ģ����Ϣ����None
        """
        if self.has_key(key):
            return self.global_dict[key]
        else:
            return None

class Hadoop_global_info(Base_global_info):
    """
    @note:��¼hadoopƽ̨��ص���Ϣ
          ���ʹ�õı��ݼ�Ⱥ��noah���Ǹ�hadoop�����ڴ���дģ����Ϣ
    """
    def __init__(self):
        Base_global_info.__init__(self)
        self.hadoop_host=""

    def get_hadoop_host(self):
        """
        @note:���hadoop_host
        """
        return self.hadoop_host

    def set_hadoop_host(self,host):
        """
        @note:����hadoop��������
        @param host:hadoop�����������
        """
        self.hadoop_host = host
        return 0

    def get_hadoop_dict_by_type(self, key):
        """
        @note:��ȡһ��ģ���Ӧ��dict
        @param key:����ģ���typeֵ
        @return :��ģ���Ӧ��dict�ʵ�,�����������ģ����Ϣ����None
        """
        if self.has_key(key):
            return self.global_dict[key]
        else:
            return None

class Std_global_info(Base_global_info):
    """
    @note:��¼��׼��ftp���ص�ַ��Ϣ��������ģ�鱸����ĳЩ�������棬��ô���ģ�����Ϣ�����õ�
    """
    def __init__(self):
        Base_global_info.__init__(self)

class Scmpf_global_info(Base_global_info):
    """
    @note:��¼scmpf  ���͵�Դ��Ϣ
    """
    def __init__(self):
        Base_global_info.__init__(self)
        self.scmpf_host=""
        self.scmpf_user=""
        self.scmpf_passwd=""
        
    def set_scmpf_host_info(self,host,user,passwd):
        """
        @note:����scmpf��host��Ϣ
        @param host:host
        @param user:user
        @param passwd:passwd
        """
        self.scmpf_host=host
        self.scmpf_user=user
        self.scmpf_passwd=passwd
        return 0

    def get_scmpf_host_info(self):
        """
        @note:����scmpf����ģ�����Ϣ
        """
        return self.scmpf_host,self.scmpf_user,self.scmpf_passwd


#��Щȫ�ֱ����Ǹ���ģ������Ҫ����Ϣ����ÿ��app���е�ʱ����Ҫ������ģ��ı����ֵ���Ϣ������˴�
#���������޸Ĵ˴�
hadoop_info = Hadoop_global_info()
std_info = Std_global_info()
scmpf_info = Scmpf_global_info()
