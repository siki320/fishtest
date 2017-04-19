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

import sys
import os.path
import socket
import inspect
import imp
from frame.lib.commonlib.kvconf import Kvconf
from frame.lib.commonlib.dlog import dlog
# ����rpyc��pythonpath
# rpyc_path = os.path.join(os.path.dirname(__file__), "../thirdlib")
rpyc_path = os.path.abspath(rpyc_path)
if rpyc_path not in sys.path:
        sys.path.append(rpyc_path)
import frame.lib.thirdlib.rpyc
from frame.lib.thirdlib.rpyc.core import consts
from frame.lib.thirdlib.rpyc.core.netref import syncreq
from frame.lib.commonlib.utils import get_abs_dir
from frame.lib.commonlib.timer import Timer2
from frame.lib.commonlib.portalloc import PortAlloc
from frame.lib.deploylib.xdsystem import XDSystem
from frame.lib.deploylib.element import Element
from frame.lib.deploylib.result import Module_Result
from frame.lib.deploylib.xdlog import XDLog
from frame.lib.deploylib.utils import ping,healthy_clients_list
from frame.lib.deploylib.xderror import XDComponentError,XDCommonError
from frame.lib.deploylib.download import HadoopDownload,StdDownload,ScmpfDownload,HudsonDownload,LocalDownload,SvnDownload,DataCenterDownload,HDFSDownload
from copy import deepcopy



class RpycTypeMixIn(object):

    DEFAULT_RPC_PORT = 60778
    RPYC_CLIENT_NUM = 0
    conn = []

    @staticmethod
    def create_component(klass, host_info, *args, **argws):
        localhostname = socket.gethostname()
        try:
            localip = socket.gethostbyname(localhostname)
        except:
            print "Cannot get local ip by hostname[%s], set ip=127.0.0.1!"%localhostname
            localip = "127.0.0.1"
        desthost = host_info["host"].strip()
        localuser = os.environ["USER"]
        client_path = os.environ.get("client_path",'.XDS_CLIENT')
        
        if (localhostname == desthost or localip == desthost or desthost == "127.0.0.1") and (host_info["user"] == "localuser" or host_info["user"] == localuser):
            host_info["host"] = localhostname
            host_info["user"] = localuser
            host_info["ip"] = localip
            host_info['client_path'] = client_path
            host_info["is_local"] = 1
            return RpycTypeMixIn.create_local_component(klass, host_info, *args, **argws)
        else:
            host_info["host"] = desthost
            host_info["ip"] = socket.gethostbyname(desthost)
            host_info["is_local"] = 0
            host_info['client_path'] = client_path
            return RpycTypeMixIn.create_remote_component(klass, host_info, *args, **argws)

    @staticmethod
    def create_local_component(klass, host_info, *args, **argws):
        instance = RpycTypeMixIn.__new__(klass)
        instance.host_info = host_info
        return instance

    @staticmethod
    def create_remote_component(klass, host_info, *args, **argws):
        RpycTypeMixIn.DEFAULT_RPC_PORT = host_info["rpyc_port"]
        client_path=host_info["client_path"]
        if not os.path.isabs(client_path):
            client_path = "/home/" + host_info["user"] + "/" + client_path
        if host_info["user"] == "root":
            RpycTypeMixIn.DEFAULT_RPC_PORT = 60779
            client_path = "/root/.XDS_CLIENT"
        if ping(host_info["ip"], int(RpycTypeMixIn.DEFAULT_RPC_PORT)) != 0:
            raise XDComponentError("can not connect to " + host_info["host"])

        RpycTypeMixIn.conn.append(frame.lib.thirdlib.rpyc.classic.connect(host_info["host"], int(RpycTypeMixIn.DEFAULT_RPC_PORT)))
        host_info['rpc_connection'] = RpycTypeMixIn.conn[RpycTypeMixIn.RPYC_CLIENT_NUM]

        RpycTypeMixIn.conn[RpycTypeMixIn.RPYC_CLIENT_NUM].modules.sys.path.insert(0,client_path)
        mod_name = klass.__module__
        cls_name = klass.__name__
        RpycTypeMixIn.RPYC_CLIENT_NUM += 1
        
        return getattr(RpycTypeMixIn.conn[RpycTypeMixIn.RPYC_CLIENT_NUM-1].modules[mod_name], cls_name).remote_create_component(klass, host_info, *args, **argws)

    @staticmethod
    def remote_create_component(klass, host_info, *args, **argws):
        mod_name = syncreq(klass, consts.HANDLE_GETATTR, '__module__')
        cls_name = syncreq(klass, consts.HANDLE_GETATTR, '__name__')
        tmpmod = __import__(mod_name, globals(), locals(), [mod_name], -1)
        klass = getattr(tmpmod, cls_name)
        instance = RpycTypeMixIn.create_local_component(klass, host_info, *args, **argws)
        instance.__init__(host=host_info["host"],user=host_info["user"], local_path=host_info["path"], *args, **argws)
        return instance

class BaseModule(RpycTypeMixIn):
    """
    @note: ����ģ��Ļ��࣬���� bs, as
    """
    def __new__(cls, host="127.0.0.1", user="localuser", local_path="./", passwd=None, rpyc_port=60778, *args, **argws):
        """
        ��ʵ����__init__ǰ����RPCģ�飬���������Զ��ʵ��������host��Ϣ�����Ӹû����ϵ�rpyc server
        """
        host_info = dict()
        host_info["host"] = host
        host_info["user"] = user
        host_info["path"] = get_abs_dir(path=local_path,exist=False)
        host_info["passwd"] = passwd
        host_info["rpyc_port"] = rpyc_port

        return cls.create_component(cls, host_info, *args, **argws)

    def __init__(self,host="127.0.0.1", user="localuser", local_path="./",instance_name=None,passwd=None,config_file=None,**args):
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
        #ģ�������������ļ�
        self.config_file = self.search_abs_path(config_file)
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

    def __getstate__(self):
        odict = self.__dict__.copy() # copy the dict since we change it
        if odict["host_info"].has_key('rpc_connection'):
            del odict["host_info"]['rpc_connection']
        if odict["portalloc"]:
            del odict["portalloc"]
        odict['port_segs'] =[]
        return odict

    def __setstate__(self,state):
        self.__dict__.update(state)
        if 0 == self.host_info["is_local"]:
            instance = RpycTypeMixIn.create_remote_component(self.__class__,self.host_info)
            for k,v in self.__dict__.items():
                instance.__dict__[k] = v
            self = instance
            self.init_handlers(dlog)

    def search_abs_path(self,element_conf):
        #modify by geshijing
        #���Ӷ������·����element �����ļ����ҹ���
        #����˳�� ��Ʒ�߾���·������Ʒ�߸�·����frameƽ����-> �����modulelib��·��-> .XDS_CLIENT��ľ���·��,�ҵ�����ֹ
        client_path_name=self.host_info["client_path"]
        if element_conf and( not os.path.isabs(element_conf)) and(not os.path.exists(element_conf)):
            #���һ���frame�����·��
            path_base_frame = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../',element_conf))
            #���һ�������obj�����·��
            path_base_obj = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(inspect.getfile(self.__class__))),element_conf))
            #���һ���.XDS_CLIENT�ľ���·��
            path_base_abs = os.path.abspath(os.path.join(os.path.expanduser("~/%s"%client_path_name),element_conf))
            #modify by hushiling01
            #����config_file���ڵ�·����ǰ����config_file�Ѿ��г�ʼֵ
            path_config_abs = None
            if self.__dict__.has_key("config_file"):
                path_config_abs = os.path.join(os.path.dirname(self.config_file),element_conf)
            if os.path.exists(path_base_frame):
                element_conf = path_base_frame
            elif os.path.exists(path_base_obj):
                element_conf = path_base_obj
            elif os.path.exists(os.path.join(os.path.expanduser("~/%s"%client_path_name),element_conf)):
                element_conf = os.path.join(os.path.expanduser("~/%s"%client_path_name),element_conf)
            elif os.path.exists(path_config_abs):
                element_conf = path_config_abs
            else:
                raise AssertionError,"Can't find any file for the relative path[%s] in [%s,%s,%s]"%(element_conf,path_base_frame,path_base_obj,path_base_abs)
        return element_conf

    def init_handlers(self,log):
        """
        @note: ��ʼ��һ��module�ĸ���handler
        @param log: ���Ļ���־����Ϊ�˰���־�����Ļ���Ļ����־��
        """
        #����instance_name������־�ļ��������û����instance_name������ֻ���һ����ģ�飬ֱ��ȥtype��
        if self.instance_name == None or self.instance_name == "":
            self.instance_name = self.type

        basepath = os.path.basename(self.host_info["path"])
        host_name = self.host_info["host"]

        if self.host_info["is_local"] == 0:
            client_path = os.path.join(os.path.expanduser('~'),self.host_info["client_path"])
            if not os.path.exists(client_path):
                os.system('mkdir -p '+client_path)
            os.chdir(client_path)

        if not self.log:
            self.log = XDLog(log, host_name + basepath + self.instance_name, self.instance_name)
            if not os.path.exists("./log"):
                os.mkdir("./log")
            #ɾ������ģ���ϴδ��ŵ���־��Ϣ��ʹ��ÿ�δ����־���汾�εģ������Ļ�����־������ɾ��
            #���Ļ���־�������д�������־
            if os.path.isfile("./log/" + self.instance_name + ".log"):
                os.remove("./log/" + self.instance_name + ".log")
            self.log.init_logger("./log/" + self.instance_name + ".log")

        #��ʼ��system,���ڵ���linux����
        self.__set_system()
        #��ʼ��download_objΪ���ʵ�Դ
        self.__set_download_obj()
        #��ʼ������element,ĿǰĬ��ֻ�а�������д��config�ļ��ͱ���Ϊ����Ҫע���
        #���һ��module�������ܶ಻ͬ��elements����ͬ��elementʹ�ò�ͬ�����ط���
        self.init_all_elements()
        self.__set_result_obj()
        return 0

    def __set_download_obj(self):
        """
        @note:init��ͬ��download handler
        """
        self.hadoop_download = HadoopDownload(self.log, \
                        self.host_info, self.type, self.retry_num)
        self.std_download = StdDownload(self.log, \
                        self.host_info, self.type, self.retry_num)
        self.scmpf_download = ScmpfDownload(self.log, \
                        self.host_info, self.type, self.retry_num)
        self.hudson_download = HudsonDownload(self.log, \
                        self.host_info, self.type, self.retry_num)
        self.local_download = LocalDownload(self.log, \
                        self.host_info, self.type, self.retry_num)
        self.svn_download = SvnDownload(self.log, \
                        self.host_info, self.type, self.retry_num)
        self.center_download = DataCenterDownload(self.log, \
                        self.host_info, self.type, self.retry_num)
        self.hdfs_download = HDFSDownload(self.log, \
                        self.host_info, self.type, self.retry_num)
        return 0

    def __set_result_obj(self):
        """
        @note:init result_obj
        """
        self.result_obj = Module_Result(type=self.type,path=self.host_info["path"],\
                        host=self.host_info["host"],user=self.host_info["user"],\
                        instance=self.instance_name)
        return 0

    def __set_system(self):
        """
        @note: �������system�������popen��ִ��shell����Ĳ���������������־��ӡ�����Ļ���Ļ����־�ͱ�����־��
        """
        self.sys = XDSystem(self.log)
        return 0

    ###����ÿ��ģ���element��ʹ��ģ���������������
    def parse_config_file(self):
        """
        @note: ���������ļ�
        @return: element_list,kv_config_file
        """
        if self.config_file == None:
            return None
        kv_config_file = Kvconf(self.config_file)
        element_list = []
        src_list =[]
        for key in kv_config_file.lines:
            if key.startswith("#"):
                continue
            if key.startswith("element_"):
                element_list.append(key.replace("element_",""))
            if key.startswith("src_"):
                src_list.append(key.replace("src_",""))
        return element_list, kv_config_file,src_list

    def init_all_elements(self):
        """
        @note: ��ʼ����module������elements
               ����ÿ��element��ʹ�õ�download����
               ע�⣺element��download�����Լ�download�ֵ��������ʱ�򸳳�ֵ
        """
        config_result = self.parse_config_file()
        if config_result == None:
                return 0
        element_list = config_result[0]
        src_list = config_result[2]
        for src in src_list:
            src_dict = eval(config_result[1].getvalue("src_" +src))
            self.reg_src(src ,src_dict)

        for one_element in element_list:
            tmp_element_dict = eval(config_result[1].getvalue("element_"+one_element))
            if tmp_element_dict.has_key('des_file'):
                tmp_element_dict['des_file'] = self.search_abs_path(tmp_element_dict['des_file'])
            self.add_element(one_element,tmp_element_dict)
        return 0

    def reg_src(self,src_name,src_dict):
        '''
        @note:ע��һ������Դ
        @param src_name:����Դ����
        @param src_dict:����Դ�ֵ�
        '''
        if not src_name in self.src_list:
            self.src_list.append(src_name)
        self.src_dict[src_name]  = src_dict

    def get_src(self,src_name):
        '''
        @note:��ȡ����Դ�ֵ��һ������
        @param src_name:����Դ����
        '''
        if self.src_dict.has_key(src_name):
            #��ʱʹ��deepcopy ��ֹ�޸���ɵ��쳣
            return deepcopy(self.src_dict[src_name])
        else:
           return {}


    def add_element(self,element_name,dest_dict):
        '''
        @note: ����һ��ģ��Ԫ��
        @param element_name:Ԫ����
        @param dest_dict:Ԫ�������ֵ�
        '''
        if not element_name in self.element_list:
            self.element_list.append(element_name)
        tmp_element = Element(name = element_name,file_path = self.config_file)
        if dest_dict["src_type"].startswith("hadoop"):
            tmp_element.downloadobj = self.hadoop_download
        elif dest_dict["src_type"].startswith("std"):
            tmp_element.downloadobj = self.std_download
        elif dest_dict["src_type"].startswith("scmpf"):
            tmp_element.downloadobj = self.scmpf_download
        elif dest_dict["src_type"].startswith("hudson"):
            tmp_element.downloadobj = self.hudson_download
        elif dest_dict["src_type"].startswith("local"):
            tmp_element.downloadobj = self.local_download
        elif dest_dict["src_type"].startswith("svn"):
            tmp_element.downloadobj = self.svn_download
        elif dest_dict["src_type"].startswith("center"):
            tmp_element.downloadobj = self.center_download
        elif dest_dict["src_type"].startswith("hdfs"):
            tmp_element.downloadobj = self.hdfs_download
        else:
            self.log.warning("type %s we do not support" %(dest_dict["src_type"]))
            raise ValueError, "Unsupported src_type"
        tmp_element.src_dict = self.get_src(dest_dict["src_type"])
        tmp_element.dst_dict =  dest_dict
        self.element_dict[element_name] = tmp_element

    def del_element(self,element_name_list):
        """
        @note:ɾ��element ���ﵽ�����ظ�element��Ŀ��
        @param element_name_list:��Ҫɾ����element�б�
        """
        for element_name in element_name_list:
            if self.element_dict.has_key(element_name):
                del self.element_dict[element_name]
            if element_name in self.element_list:
                self.element_list.remove(element_name)
        return 0

    def check_ip_local_port_range(self):
        """
        @note:ԭ����clientռ����server�Ķ˿ڣ�����ͨ�������������
              1����/proc/sys/net/ipv4/ip_local_port_range
              2���жϵڶ��е������Ƿ����61000��������ڵĻ��ͱ�����
              3�����ص�ǰģ�����ڻ�����/proc/sys/net/ipv4/ip_local_port_range ֵ
        """
        ip_local_port_range = self.sys.xd_system("cat /proc/sys/net/ipv4/ip_local_port_range", output = "true")[1]
        max_port_kernel = ip_local_port_range.split('\t')[1][:-1]
        kernel_ip_local_port_range = ip_local_port_range.splitlines()
        if max_port_kernel.isdigit() == False:
            self.log.warning("maybe you can not cat /proc,using default staring port for port adaptive")
            begin_port = 61100
        else:
            begin_port = int(max_port_kernel)+100
        #if int(max_port_kernel) > 61000:
            #self.log.critical("yifeng is tracing")
            #raise XDCommonError,"ip_local_port_range is larger than 61000"
        #return kernel_ip_local_port_range
        return begin_port,65500

    ###ÿ��ģ�鶼����������·���###
    def port_adaptive(self):
        '''
        @note:ʹ���ڱ��㷨���ж˿�����Ӧ
        '''
        begin_port,end_port = self.check_ip_local_port_range()
        #�ں����н��г�ʼ��������ظ�����ʱ�˿ڷ�����������
        if self.__dict__.get("portalloc",None):
            for port_seg in self.port_segs:
                self.portalloc.freePortSeg(port_seg)
            self.port_segs = []
            del self.portalloc
        self.port_list = []
        self.portalloc = PortAlloc(begin_port, end_port, 10)
        port_seg = self.portalloc.allocPortSeg()
        self.port_segs.append(port_seg)
        while(len(self.port_list)<self.port_num):
            try:
                port = self.portalloc.allocPort(port_seg)
                self.port_list.append(port)
            except Exception, e:
                self.log.warning('the module are using more than 9 ports')
                port_seg = self.portalloc.allocPortSeg()
                self.port_segs.append(port_seg)
        self.log.info('the module are using ports[%s]',str(self.port_list))
        return 0

    def get_listen_port(self):
        """
        @note:���ģ��ļ����˿�
        """
        return self.listen_port

    def set_listen_port(self):
        """
        @note:����ģ��ļ����˿�,�˿�����Ӧ����ô˺������ö˿�
        """
        return 0

    def del_relation(self,module):
        """
        @note: �������ݵ����Ѿ����ɵ�����module��ʵ��,�ú�����Ϊ��ɾ��������ϵʹ��
               �������ñ�ģ������й�����ϵ��ģ����Ϣ
        @param module: ����ģ�����
        """
        if module in self.module_rel_set:
            self.module_rel_set.remove(module)

    def add_relation(self,module):
        """
        @note: �������ݵ����Ѿ����ɵ�����module��ʵ��,�ú�����Ϊ�˽���������ϵʹ��
               �������ñ�ģ������й�����ϵ��ģ����Ϣ
        @param module: ����ģ�����
        """
        self.module_rel_set.append(module)

    def build_relation(self):
        """
        @note: ����������ϵ
        """
        dict_set = {}
        #for dashboard
        self.result_obj.set_module_rel_set(self.module_rel_set)
        for module_type in self.all_rel_module:
            dict_set[module_type] = []

        for module_obj in self.module_rel_set:
            module_type = getattr(module_obj,"type")
            dict_set[module_type].append(module_obj)

        #self.debug("set relation %s\nmodule_rel_set:%s" %(str(dict_set), str(self.module_rel_set)) )
        for module_type in dict_set:
            if len(dict_set[module_type]) == 0:
                continue    
            if hasattr(self,"set_" + module_type + "_relation"):
                getattr(self,"set_" + module_type + "_relation")(dict_set[module_type])
            else:
                getattr(self,"set_relation")(dict_set[module_type])

        return 0

    def download(self):
        """
        @note: ����
        """
        download_time = Timer2()
        download_time.start()
        for one_element in self.element_list:
            if self.element_dict.has_key(one_element):
                self.element_dict[one_element].download()
            else:
                self.log.warning("element_%s was delete from self.element_dict"%(one_element))
        download_time.end()
        #��λΪ��,�ռ������Ϣ
        self.result_obj.set_download_time(download_time._starttime,download_time._interval)
        self.result_obj.element_dict = self.element_dict
        return 0

    def predownload(self):
        """
        @note: Ԥ��������ǰ��
        """
        return 0


    def preprocess(self):
        """
        @note: Ԥ�������غ�
        """
        return 0

    def localize(self):
        """
        @note: ���ػ�
        """
        return 0

    def postprocess(self):
        """
        @note: �����������ӹ�ϵ��
        """
        return 0

    def start(self):
        """
        @note: ����ģ��
        """
        return 0

    def stop(self):
        """
        @note: ֹͣģ��
        """
        return 0

    def restart(self):
        """
        @note: ����ģ��
        """
        return 0

    def clean(self):
        """
        @note: ����ģ��
        """
        return 0

    def set_bak_dir(self,bakdir = None):
        '''
        @note ����ģ�鱸��·��������д�豣֤���ص��Ǿ���·��
        '''
        if bakdir == None:
            #Ĭ��ʹ��ģ�������bak_dir·��,����������ʹ�õ�ǰ·��
            if self.__dict__.has_key('bak_dir'):
                bak_dir = self.bak_dir
            else:
                bak_dir = './bakup'
        else:
            bak_dir = bakdir
        self.bak_dir = os.path.abspath(bak_dir)
        return self.bak_dir

    def backup(self,include =[],exclude =[]):
        """
        @note������ģ��,������·�����ȼ����ڲ�������·��
        """
        #��ȡ���ݵ�·��
        bak_dir = self.set_bak_dir()
        path_pair = (self.host_info["path"],'')
        while path_pair[1] == '':
            path_pair = os.path.split(path_pair[0])
        self.log.info("Start to back up module: %s to %s",self.host_info["path"],bak_dir)
        #������Ҫ������·��
        includestr = ""
        for includelist in include:
           includestr += " --include='%s'"%str(os.path.join(path_pair[1],includelist))
        excludestr= ''
        for blacklist in exclude:
            excludestr += " --exclude='%s'"%str(os.path.join(path_pair[1],blacklist))
        cmd = "rsync --delete -a %s %s %s %s"%(includestr,excludestr,self.host_info["path"],bak_dir)
        self.sys.xd_system(cmd,output = True)
        self.log.info("Finished backing up module by cmd: [%s]",cmd)
        return 0

    def restore(self,isforce = True):
        '''
        @note���ӱ����лָ�ģ��
        ע�⣺Ĭ�ϻ�ɾ�����еĸĶ�,������־
        ��isforceΪfalseʱ��ֻ�ָ����ݲ��ֵ�����
        '''
        #��ȡ���ݵ�·��
        bak_dir = self.set_bak_dir()
        path_pair = (self.host_info["path"],'')
        while path_pair[1] == '':
            path_pair = os.path.split(path_pair[0])

        self.log.info("Start to restore module from: %s to %s",bak_dir,self.host_info["path"])
        srcpath = os.path.join(bak_dir,path_pair[1])+'/'
        if os.path.exists(srcpath) == False:
            self.log.error("Source path do not exist [%s], you need to backup before restore")
            return -1
        if isforce:
            cmd ="rsync --delete -a %s %s"%(os.path.join(bak_dir,path_pair[1])+'/',self.host_info["path"])
        else:
            cmd ="rsync -a %s %s"%(os.path.join(bak_dir,path_pair[1])+'/',self.host_info["path"])
        self.sys.xd_system(cmd,output = True)
        self.log.info("Finished restore module by cmd: [%s]"%cmd)
        return 0

    #�⼸����������������;�ķ�������ϸ�뿴˵��
    def retry_func(self,func,retry_num=3):
        """
        @author:guoan
        @note: ����һЩ��������ϣ������һ��Ҫִ�гɹ�����������ṩretry�Ĺ���
        @param func:������
        @param retry_num:���Դ���
        """
        self.log.debug("we will retry %s times"%(retry_num))
        ret = 0
        if hasattr(self,func):
            tmp_func = getattr(self,func)
        else:
            self.log.warning("method %s is not exit,please make attention"%(func))
            return
        for i in range(retry_num):
            if tmp_func() == 0:
                self.log.debug("exec %s successfuly"%(func))
                ret = 0
                break
            else:
                self.log.warning("now we retry %s the %s time"%(func,str(i+1)))
                continue
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

