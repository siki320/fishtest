# -*- coding: GB18030 -*-
"""
@author: songyang
@modify: guoan
@modify: maqi
@modify: geshijing
@date: Nov 29, 2011
@summary: 负责环境搭建的统一调度
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
# 增加rpyc到pythonpath
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
    @note: 所有模块的基类，例如 bs, as
    """
    def __new__(cls, host="127.0.0.1", user="localuser", local_path="./", passwd=None, rpyc_port=60778, *args, **argws):
        """
        在实例被__init__前调用RPC模块，创建组件的远程实例，根据host信息，连接该机器上的rpyc server
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
        @note: host, user, local_path都在init之前被赋值到self.host_info的dict中了，不需要再init中赋值
        """
        #每个类都有一个type属性，这个属性对应传入词典的key值
        self.type = None
        #这个属性控制wget命令失败的时候重试几次
        self.retry_num = 3
        #配置本模块有多少的端口
        self.port_num = 0
        self.listen_port = None
        self.port_list = []
        #包含下游具体模块实例,表示一个搭建场景下 本模块注册的下游实例（实例级别的）
        self.module_rel_set = []
        #每个模块的外围模块对象,表示本模块 下游一共有多少模块
        self.all_rel_module = []
        #对于某些模块需要搭建多个的时候，可以通过instance_name进行区别
        self.instance_name = instance_name
        #log对象，用于各个模块写log
        self.log = None
        #调用linux系统命令的handler
        self.sys = None
        #模块自描述配置文件
        self.config_file = self.search_abs_path(config_file)
        #每个模块的自描述，默认含有bin conf data,支持扩展，可以到达文件的粒度
        self.element_dict = {}
        #用于element下载的保序
        self.element_list = []
        #模块下载源的字典
        self.src_dict={}
        #模块下载源的原信息保存
        self.src_list=[]

        #用于记录搭建的详细信息，供dashboard展示
        self.result_obj = None
        #用于端口自适应
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
        #增加对于相对路径的element 配置文件查找功能
        #查找顺序 产品线绝对路径（产品线根路径与frame平级）-> 相对于modulelib的路径-> .XDS_CLIENT后的绝对路径,找到后终止
        client_path_name=self.host_info["client_path"]
        if element_conf and( not os.path.isabs(element_conf)) and(not os.path.exists(element_conf)):
            #查找基于frame的相对路径
            path_base_frame = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../../',element_conf))
            #查找基于自身obj的相对路径
            path_base_obj = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(inspect.getfile(self.__class__))),element_conf))
            #查找基于.XDS_CLIENT的绝对路径
            path_base_abs = os.path.abspath(os.path.join(os.path.expanduser("~/%s"%client_path_name),element_conf))
            #modify by hushiling01
            #查找config_file所在的路径，前提是config_file已经有初始值
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
        @note: 初始化一个module的各种handler
        @param log: 中心机日志对象，为了把日志打到中心机屏幕和日志中
        """
        #根据instance_name决定日志文件名，如果没设置instance_name，表明只搭建了一个该模块，直接去type名
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
            #删除各个模块上次搭建存放的日志信息，使得每次搭建的日志保存本次的，而中心机的日志不进行删除
            #中心机日志保存所有搭建情况的日志
            if os.path.isfile("./log/" + self.instance_name + ".log"):
                os.remove("./log/" + self.instance_name + ".log")
            self.log.init_logger("./log/" + self.instance_name + ".log")

        #初始化system,用于调用linux命令
        self.__set_system()
        #初始化download_obj为合适的源
        self.__set_download_obj()
        #初始化各个element,目前默认只有按规则填写到config文件就被认为是需要注册的
        #针对一个module，包含很多不同的elements，不同的element使用不同的下载方法
        self.init_all_elements()
        self.__set_result_obj()
        return 0

    def __set_download_obj(self):
        """
        @note:init不同的download handler
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
        @note: 设置类的system对象替代popen等执行shell命令的操作，并将错误日志打印到中心机屏幕、日志和本地日志中
        """
        self.sys = XDSystem(self.log)
        return 0

    ###设置每个模块的element，使得模块具有自描述能力
    def parse_config_file(self):
        """
        @note: 解析配置文件
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
        @note: 初始化该module的所有elements
               包括每个element所使用的download对象
               注意：element的download对象，以及download字典是在这个时候赋初值
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
        @note:注册一个下载源
        @param src_name:下载源名字
        @param src_dict:下载源字典
        '''
        if not src_name in self.src_list:
            self.src_list.append(src_name)
        self.src_dict[src_name]  = src_dict

    def get_src(self,src_name):
        '''
        @note:获取下载源字典的一个拷贝
        @param src_name:下载源名字
        '''
        if self.src_dict.has_key(src_name):
            #暂时使用deepcopy 防止修改造成的异常
            return deepcopy(self.src_dict[src_name])
        else:
           return {}


    def add_element(self,element_name,dest_dict):
        '''
        @note: 增加一个模块元素
        @param element_name:元素名
        @param dest_dict:元素属性字典
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
        @note:删除element ，达到不下载该element的目的
        @param element_name_list:需要删除的element列表
        """
        for element_name in element_name_list:
            if self.element_dict.has_key(element_name):
                del self.element_dict[element_name]
            if element_name in self.element_list:
                self.element_list.remove(element_name)
        return 0

    def check_ip_local_port_range(self):
        """
        @note:原因是client占用了server的端口，所以通过这个方法防范
              1）读/proc/sys/net/ipv4/ip_local_port_range
              2）判断第二列的数字是否大于61000，如果大于的话就报错了
              3）返回当前模块所在机器的/proc/sys/net/ipv4/ip_local_port_range 值
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

    ###每个模块都必须包含以下方法###
    def port_adaptive(self):
        '''
        @note:使用哨兵算法进行端口自适应
        '''
        begin_port,end_port = self.check_ip_local_port_range()
        #在函数中进行初始化，解决重复调用时端口分配出错的问题
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
        @note:获得模块的监听端口
        """
        return self.listen_port

    def set_listen_port(self):
        """
        @note:设置模块的监听端口,端口自适应会调用此函数设置端口
        """
        return 0

    def del_relation(self,module):
        """
        @note: 参数传递的是已经生成的其他module的实例,该函数是为了删除关联关系使用
               作用是让本模块包含有关联关系的模块信息
        @param module: 下游模块对象
        """
        if module in self.module_rel_set:
            self.module_rel_set.remove(module)

    def add_relation(self,module):
        """
        @note: 参数传递的是已经生成的其他module的实例,该函数是为了建立关联关系使用
               作用是让本模块包含有关联关系的模块信息
        @param module: 下游模块对象
        """
        self.module_rel_set.append(module)

    def build_relation(self):
        """
        @note: 建立关联关系
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
        @note: 下载
        """
        download_time = Timer2()
        download_time.start()
        for one_element in self.element_list:
            if self.element_dict.has_key(one_element):
                self.element_dict[one_element].download()
            else:
                self.log.warning("element_%s was delete from self.element_dict"%(one_element))
        download_time.end()
        #单位为秒,收集搭建的信息
        self.result_obj.set_download_time(download_time._starttime,download_time._interval)
        self.result_obj.element_dict = self.element_dict
        return 0

    def predownload(self):
        """
        @note: 预处理（下载前）
        """
        return 0


    def preprocess(self):
        """
        @note: 预处理（下载后）
        """
        return 0

    def localize(self):
        """
        @note: 本地化
        """
        return 0

    def postprocess(self):
        """
        @note: 后处理（建立连接关系后）
        """
        return 0

    def start(self):
        """
        @note: 启动模块
        """
        return 0

    def stop(self):
        """
        @note: 停止模块
        """
        return 0

    def restart(self):
        """
        @note: 重启模块
        """
        return 0

    def clean(self):
        """
        @note: 清理模块
        """
        return 0

    def set_bak_dir(self,bakdir = None):
        '''
        @note 设置模块备份路径，若重写需保证返回的是绝对路径
        '''
        if bakdir == None:
            #默认使用模块自身的bak_dir路径,若不存在则使用当前路径
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
        @note：备份模块,包含的路径优先级高于不包含的路径
        """
        #获取备份的路径
        bak_dir = self.set_bak_dir()
        path_pair = (self.host_info["path"],'')
        while path_pair[1] == '':
            path_pair = os.path.split(path_pair[0])
        self.log.info("Start to back up module: %s to %s",self.host_info["path"],bak_dir)
        #设置需要包含的路径
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
        @note：从备份中恢复模块
        注意：默认会删除所有的改动,包括日志
        当isforce为false时，只恢复备份部分的内容
        '''
        #获取备份的路径
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

    #这几个方法是有特殊用途的方法，详细请看说明
    def retry_func(self,func,retry_num=3):
        """
        @author:guoan
        @note: 对于一些方法我们希望他们一定要执行成功，这个函数提供retry的功能
        @param func:方法名
        @param retry_num:重试次数
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
        @note: 通过module load对应的client lib
        @param rel_path:相对于client path的lib路径
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

