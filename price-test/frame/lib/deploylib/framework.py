# -*- coding: GB18030 -*-
"""
@author: songyang
@modify: youguiyan01
@modify: maqi
@modify: xuwei01
@summary: 负责环境搭建的统一调度
@version: 1.1.0.0
"""

import inspect
import string
import os
import sys
import ConfigParser
import pickle
import socket
import traceback
from copy import deepcopy
from frame.lib.commonlib.dlog import dlog
from frame.lib.commonlib.utils import get_abs_dir,get_current_path
from frame.lib.commonlib.timer import Timer2

from frame.lib.deploylib.xdsystem import XDSystem
from frame.lib.deploylib.basemodule import BaseModule,RpycTypeMixIn
from frame.lib.deploylib.xdhost import XDHost
from frame.lib.deploylib.utils import ping
from frame.lib.deploylib.xderror import XDFrameError
from frame.lib.deploylib.confparser import EnvConfigHelper
from frame.lib.deploylib.result import Env_result
from frame.lib.commonlib.portalloc import PortAlloc

class Env(object):
    """
    @note: 负责环境的统一调度，包括各个模块的搭建，建立关联关系，端口自适应等
    """
    def __init__(self,log=dlog,auto_dispatch=False,auto_module_path=False):
        """
        @note: 基本信息的初始化，主要是变量的声明
        """
        #存放模块的详细信息，包括模块名，模块所在的host，user, path，和模块类型
        self.module_base = []
        self.log = log
        self.sys = XDSystem(self.log)
        self.conf = None
        self.topology_file = None
        self.topology_file_dir = None
        self.is_inited = False
        self.init_dashboard = False
        self.bash_profile_list=[]
        #env收集信息的容器类
        self.env_result = Env_result()

        # 模块启动顺序列表，仅用于按拓扑启动/关闭模块
        self.module_start_seq = []

        self.host_dict = {}
        self.module_host_require = {}
        self.atd_jobid = None
        self.module_info_dict = {}
        self.topo_info = []

        # 生成python path的文件夹的名称
        self.python_portalloc = PortAlloc(61000, 65500, 10)
        python_port = self.python_portalloc.allocPortSeg()
        localhostname = socket.gethostname()
        if not auto_dispatch:
            self.xds_client_path = ".XDS_CLIENT"
        else:
            self.xds_client_path = ".XDS_CLIENT/" + localhostname + "_" + str(python_port)
        if not auto_module_path:
            self.xds_module_path = "XDS_CLIENT"
        else:
            self.xds_module_path = "XDS_CLIENT/" + localhostname + "_" + str(python_port)
        self.log.info("set xds_client_path [%s] ",self.xds_client_path)

        #使用xstp分配机器
        self.is_xstp = False
        self.xstp_host_info_list = []

    def init_global(self,global_dict):
        '''
        @author:    geshijing
        @note:
            初始化可能需要使用的环境变量主要包括以下内容
            #xds_framelib_path: dts frame path
            #xds_modulelib_path:dts module path
            #xds_force_dispatch:true or false 设置是否分发代码，默认强制分发
            #xds_force_rpyc_start:ture or False 设置是否启动远程rpyc服务，默认强制启动
            #which_to_dispatch:传入类似xds_framelib_path，之间以空格隔开，用于支持多路径传输
            #这里使用的相对路径均是相对于app 文件所在的目录
            #这里与topy 文件使用的响度路径不一样，topy文件中使用的相对路径是相对于 topy 文件本身的
        '''
        self.log.info("Init global info [%s]"%str(global_dict))
        base_path = os.path.join(os.path.dirname(os.path.realpath(inspect.getfile(self.__class__))))
        for key in global_dict:
            if key.endswith("_path"):
                apath = global_dict[key]
                if not os.path.isabs(apath):
                    apath = os.path.join(base_path,apath)
                os.environ.update({key:apath})
            else:
                os.environ.update({key:global_dict[key]})
        os.environ.update({"client_path":self.xds_client_path})
        return 0

    def reg_host_info(self,host_name,usr,passwd):
        '''
        @author:    geshijing
        @note:
            注册机器信息
        '''
        if host_name == "ATD_AUTO":
            return
        host_sign = host_name +usr
        if self.host_dict.has_key(host_sign):
            return self.host_dict[host_sign]
        else:
            host = XDHost(host_name,usr,passwd,self.xds_client_path)
            self.host_dict[host_sign] = host
            return host

    def reg_host_in_module(self,module_info):
        '''
        @author: geshijing
        @note:
            自动申请机器，新增的接口，从模块字典中获取需要的机器信息
            添加的机器信息会在init_hosts中申请机器
        '''
        if module_info["host_name"] !="ATD_AUTO":
            return
        name = module_info["module_name"]
        #atd分配的路径看上去暂时没有用
        cpucore_require = int(module_info.get("cpuCoreNum",'0'))
        mem_require = int(module_info.get("mem",'0'))
        disk_require = int(module_info.get("disk",'0'))
        #不使用atd分配的端口
        port_num = 0
        is_exclusive = int(module_info.get("exclusive",'0'))
        workdir = ''
        expected_host = ''
        optimize_type = ''
        modconst = {
            "name": name, "cpucore_require": cpucore_require, "mem_require": mem_require,
            "disk_require": disk_require, "port_num": port_num, "is_exclusive": is_exclusive,
            "workdir": workdir,"expected_host": expected_host, "optimize_type": optimize_type
            }
        self.module_host_require[name] = modconst

    def _acquire_hosts(self):
        '''
        @note： 申请测试机
        '''
        return

    def add_host(self,host_name,user_name,password):
        '''
        @author:geshijing
        @note:注册并且初始化一个新的测试机
        '''
        host = self.reg_host_info(host_name.strip(),user_name,password)
        if host:
            host.set_log_sys(self.log,self.sys)
            host.build_xds_client()
        else:
            self.log.critical("Reg Host Failed. host_name:[%s],user_name:[%s],password:[%s]"%(host_name,user_name,password))

    def init_hosts(self):
        '''
        @author:    geshijing
        @note:
            申请机器
            初始化各个机器
            主要内容：
            建立信任关系
            分发所需的数据
            启动RPYC
        '''
        #调用atd接口申请机器
        self._acquire_hosts()
        #初始化所有的测试机
        for host in self.host_dict:
            self.host_dict[host].set_log_sys(self.log,self.sys)
            self.host_dict[host].build_xds_client()


    def release_atd_resource(self):
        '''
        @author: geshijing@XX
        @note:
            释放已经申请的机器
        '''
        if self.atd_jobid:
            atd_username = os.environ.get('ATD_USRENAME',None)
            atd_server  = os.environ.get('ATD_SERVER',None)
            if not atd_username:
                raise LookupError,"Please Set ATD_USERNAME in the conf file"
                return
            service = None
            if atd_server:
                service = MachineService(user_name=atd_username,server_host = atd_server)
            else:
                service = MachineService(user_name=atd_username)
            service.release(self.atd_jobid)
            self.atd_jobid = None

        

    def free_module(self,module_name):
        '''
        @author: geshijing
        @note:
            前面有怪兽，小心使用
            删除环境中的一个模块
        '''
        if not self.module_info_dict.has_key(module_name):
            return
        module_info = self.module_info_dict[module_name]
        del self.module_info_dict[module_name]
        for one_module in self.module_info_dict:
            self.unrelate_module(one_module,module_name)
        module_del = None
        for one_module in self.module_base:
            if one_module["instance_name"] == module_name:
                module_del = one_module
        if module_del:
            self.module_base.remove(module_del)


    def reg_module_info(self,module_info):
        '''
        @note: 注册模块信息，以便后续可以实例化模块
        @param module_info: 模块信息字典
        '''
        if module_info['user'] == "localuser":
            import getpass
            module_info['user'] = getpass.getuser()
        module_sign = module_info["module_name"]
        if self.module_info_dict.has_key(module_sign):
            raise KeyError,"Muti-module with same name%s"%module_sign
        module_info['client_path'] = self.xds_client_path
        if not os.path.isabs(module_info['remote_path']):
            module_info['remote_path'] = '/home/%s/%s/%s'%(module_info['user'],self.xds_module_path,module_info['remote_path'])
        self.module_info_dict[module_sign] = module_info

    def instantiate_module(self,module_info):
        '''
        @author:    geshijing
        @note:      实例化模块对象（远程的对象使用RPYC实例化），在实例化之前需要调用reg_module_info注册模块信息
        @param module_info: 模块信息
        '''
        #需要注册的模块名，如bdbs1
        module_name  = module_info["module_name"]
        class_name = module_info["class_name"]

        #需要导入的模块,比如Novabs映射到nova_bs.Novabs，那么需要from nova_bs import Novabs
        from_module = ".".join(self.module_name_dict[class_name].split(".")[0:-1])
        import_module = self.module_name_dict[class_name].split(".")[-1]
        #sys.path.append(os.path.expanduser("~/.XDS_CLIENT"))

        tmpmod = __import__(from_module,globals(),locals(),[import_module],-1)

        #创建对象,这里有变量名是动态的
        setattr(self,module_name,getattr(tmpmod,import_module)(instance_name=module_name,config_file=module_info["conf_file"],local_path=module_info["remote_path"],
                host=module_info["host_name"],user=module_info["user"],passwd=module_info["password"]))
        #注册对象
        self._register_module(getattr(self,module_name))

    def instantiate_modules(self):
        '''
        @author:    geshijing
        @note:      批量实例化模块对象，调用instantiate_module方法
        '''
        for module in self.module_info_dict:
            self.instantiate_module(self.module_info_dict[module])


    def relate_module(self,module_upstream,module_downstream):
        """
        @author:    youguiyan01
        @note:      添加关联关系
        """
        up_module_obj = getattr(self, module_upstream)
        down_module_obj = getattr(self, module_downstream)
        up_module_obj.add_relation(down_module_obj)
        if not (module_upstream,module_downstream) in self.topo_info:
            self.topo_info.append((module_upstream,module_downstream))
        return 0

    def unrelate_module(self,module_upstream,module_downstream):
        """
        @author:    geshijing
        @note:      删除关联关系
        """
        up_module_obj = getattr(self, module_upstream)
        down_module_obj = getattr(self, module_downstream)
        up_module_obj.del_relation(down_module_obj)
        if (module_upstream,module_downstream) in self.topo_info:
            self.topo_info.remove((module_upstream,module_downstream))
        return 0

    def set_module_name_dict(self,module_name_dict):
        """
        @author:    youguiyan01
        @note:      设置模块字典
            比如我们以前需要在app中写入,这样，我们就可以直接使用Novabs
            from novalib.bs.bs import Novabs
            那么现在我们只需要写入
            key:操作类的名，Novabs
            value:操作类所在的具体位置(包括文件路径),novalib.bs.bs.Novabs
            就可以了
        """
        self.module_name_dict = module_name_dict

    def __getstate__(self):
        odict = self.__dict__.copy()
        del odict["log"]
        del odict["sys"]
        if odict["python_portalloc"]:
            del odict["python_portalloc"]
        return odict

    def __setstate__(self,state):
        self.__dict__.update(state)
        self.log = dlog
        self.sys = XDSystem(self.log)
        self.python_portalloc = PortAlloc(61000, 65500, 10)

    def init_modules(self):
        """
        @note:App程序在此生成模块对象
        """
        pass


    def _register_modules(self):
        """
        @note:自动注册模块
        """
        for item in dir(self):
            attr = getattr(self, item)
            if isinstance(attr,BaseModule):
                self._register_module(attr)

    def _register_module_info(self,module_info):
        '''
        @note: 使用reg_module_info和instantiate_module注册并且实例化一个模块
        '''
        self.reg_module_info(module_info)
        self.instantiate_module(module_info)

    def _register_module(self,module):
        """
        @note:      注册需要搭建的模块对象和Log对象
        @param:     module:模块对象
                    log:日志对象
        @return:    0:成功
                    1:失败
        """
        #每一个对象都进行handlers的初始化
        if hasattr(module,"init_handlers") and getattr(module, "init_handlers")(self.log) != 0:
            self.log.critical("init_handlers error!")
            return 1

        #把模块的详细信息添加到列表中
        self.module_base.append({"module":module,
                                 "host":module.host_info["host"],
                                 "user":module.host_info["user"],
                                 "path":module.host_info["path"],
                                 "type":module.type,
                                 "instance_name":module.instance_name
                                 })

        self.log.info("module:%s  module_host:%s" %(str(module.instance_name),str(module.host_info["host"])))
        return 0

    def get_module_by_instance_name(self,instance_name):
        """
        @note:     按照instance_name来获得具体的module对象，注意instance_name的赋值逻辑是这样的：
                   1.按照init module的instance_name参数设置赋值
                   2.如果没有给instance_name赋值的话，默认使用type作为instance_name
        @param     instance_name: 模块实例名，每个module唯一
        @return:   module \ 如果没有找到的话返回空
        """
        for module_info in self.module_base:
            if (module_info["instance_name"] == instance_name ):
                return module_info["module"]
            else:
                continue
        return

    def _port_adaptive(self,start_port = 61000):
        """
        @note: 端口自适应,分成三步，收集占用端口，计算可用端口，分配可用端口
        """
        for module_dict in self.module_base:
            getattr(module_dict["module"],"port_adaptive")()
            getattr(module_dict["module"],"set_listen_port")()
            self.log.info("set %s port : %s" ,str(getattr(module_dict["module"],"type")) \
                    ,str(getattr(module_dict["module"],"get_listen_port")()))
        return 0


    def update(self,module_list):
        """
        @note: 局部更新,重建局部连接关系
        module_list:更改过的模块列表
        """
        if not isinstance(module_list,list):
            module_list = [module_list]

        #获取所有影响的上游模块
        all_affected_modules = self._get_affected_modules(module_list)

        #重建模块连接关系
        if not all_affected_modules == []:
            modules_str = ""
            affected_modules_str = ""
            for module in module_list:
                modules_str += str(getattr(module,"type")) + " "
            for module in all_affected_modules:
                affected_modules_str += str(getattr(module,"type")) + " "
            self.log.info("Update modules:[%s] by [%s]",affected_modules_str, modules_str)

            self.single_thread_run("build_relation",all_affected_modules)
        else:
            self.log.warning("No module need to update")

    def _get_affected_modules(self,module_list):
        '''
        @note: 获取所有影响到的上游模块
        '''
        all_affected_modules = []
        for module_dict in self.module_base:
            module_rel_set = module_dict["module"].module_rel_set
            if set(module_rel_set) & set(module_list):
                all_affected_modules.append(module_dict["module"])
        return all_affected_modules

    def get_app_filename(self):
        """
        @note: 获取当前app的执行文件名,获取调度的主入口文件名
        """
        stack =traceback.extract_stack()
        if len(stack) >=2:
            func = stack[0][0]
        return func

    def get_type_name(self):
        '''
        @note: 获取当前的app的类型名
        '''
        return "%s.%s"%(type(self).__module__,type(self).__name__)

    def set_attr_for_dashboard(self,product="ecom",appname='defaultapp'):
        """
        @note: 开启向sql发送请求的开关
               设置app\product的名字
        """
        self.env_result.set_env_info(product,appname,self.get_app_filename(),self.get_type_name())
        self.init_dashboard = True

    def collect_module_results(self):
        """
        @note: 收集各个子模块的运行结果
        """
        #清空现有的模块搭建记录
        self.env_result.clear_module_info()
        for module_info in self.module_base:
            self.env_result.collect_module_result(module_info["module"].result_obj)

    def save_result_to_sql(self):
        """
        @note: 1、save one record for this app
               2、save many records for modules
               3、save topo info for this app
        """
        try:
            self.env_result.dump_to_db()
        except:
            print "mysql server is downing ,please wait for a moment!!!"

    def init_env(self):
        """
        @note:这个函数产生的原因是由于删除element的需要
              如果需要使用del_element函数，请先调用该函数
        """
        self._parse_topology(self.topology_file_dir,self.topology_file)
        self.is_inited = True

    def deploy(self,is_download=True,is_xstp=False):
        self.is_xstp = is_xstp
        deploy_time = Timer2()
        deploy_time.start()
        if not self.is_inited:
            self._parse_topology(self.topology_file_dir,self.topology_file)
            self.is_inited = True
        if is_download:
            self.single_thread_run("predownload")
            self.single_thread_run("download")
        self.single_thread_run("preprocess")
        self._port_adaptive()
        self.single_thread_run("localize")
        self.single_thread_run("build_relation")
        self.single_thread_run("postprocess")
        deploy_time.end()
        self.env_result.set_deploy_time(deploy_time._starttime,deploy_time._interval)
        if self.init_dashboard == True:
            self.collect_module_results()
            self.save_result_to_sql()


    def deploy_by_topology(self,is_download=True):
        '''
        @note:已经淘汰的接口，请直接使用deploy
        '''
        return self.deploy(is_download)

    def start(self):
        self.single_thread_run("start")

    def stop(self):
        self.single_thread_run("stop")

    def restart(self):
        self.single_thread_run("restart")

    def clean(self):
        self.single_thread_run("clean")

    def backup(self):
        #多线程调用模块的备份方法
        self.multi_thread_run("backup")

    def dump(self,filepath):
        '''
        对象序列化
        '''
        fd = file(filepath, 'wb')
        pickle.dump(self,fd,True)
        fd.close()

    def set_topology_file(self, file=''):
        '''
        @note: 设置从哪里读取拓扑关系的文件
        '''
        if False == os.path.exists(file):
            self.log.critical("Input invalid filename: %s" % file)
            return 1

        self.topology_file = os.path.basename(file)
        self.topology_file_dir = get_abs_dir(os.path.dirname(file)) + '/'

        return 0

    def set_hostinfo_file(self, hfile=''):
        '''
        @note: 设置从哪里读取xstp分配的机器信息
        '''
        if False == os.path.exists(hfile):
            self.log.critical("Input invalid filename: %s" % hfile)
            raise Exception,"%s does not exist!"%hfile
        self.xstp_host_info_list = []
        hostfile = file(hfile)
        for line in hostfile:
            self.xstp_host_info_list.append({})
            fields = line.rstrip().split("\t")
            for field in fields:
                k,v = field.split(":")
                self.xstp_host_info_list[-1][k] = v
        hostfile.close()

        return 0

    def _parse_topology(self,file_dir,file):
        '''
        @author:maqi
        @note: 处理拓扑配置文件
        '''
        self.init_modules()
        #if not self.topology_file :
        #    return
        self.conf = EnvConfigHelper.get_conf(self.topology_file_dir,self.topology_file)
        if self.conf is None or self.conf.type == 'sm':
            return self._parse_topology_sm()
        elif self.conf.type == 'mm' or self.conf.type == 'mmub':
            return self._parse_topology_mm()
        else:
            raise XDFrameError,'topology file type error'

    def _parse_topology_sm(self):
        #生成模块并注册
        self._register_modules()
        if self.conf is None:
            return 0
        #创建关联关系
        topology_info_list = self.conf.parse_topology()
        for topology_info in topology_info_list:
            self._relate_module(topology_info)
        return 0

    def _parse_topology_mm(self):
        """
        @author:youguiyan01
        @param  topology_file:拓扑结构文件
        @note:  解析拓扑结构，根据拓扑结构，创建相应的对象，并建立关联关系
        """
        #获取远程搭建需要的环境变量信息
        self._set_remote_bash_profile(self.conf)
        #解析module name dict 信息
        if self.conf.get_conf_version() == "3":
            module_name = self.conf.parse_module_name_dict()
            if module_name != None:
                self.module_name_dict = module_name
        #解析模块信息
        host_info_list,module_info_list = self.conf.parse_host_module()

        if host_info_list == None:
            return 1

        for host_info in host_info_list:
            self.reg_host_info(host_info["host_name"].strip(),host_info["user"],host_info["password"])
        #根据xstp更新机器列表,和模块信息
        if self.is_xstp:
            for host_info in self.xstp_host_info_list:
                self.reg_host_info(host_info["host"].strip(),host_info["applyUser"],host_info["applyPassword"]) 
                for  module_info in module_info_list:
                    if module_info["module_name"]==host_info["moduleName"]:
                        module_info["host_name"] = host_info["host"].strip()
                        module_info["user"] = host_info["applyUser"]
                        module_info["password"] = host_info["applyPassword"]
                        module_info["remote_path"] = host_info["workPath"]
        if module_info_list == None:
            return 1

        #自动创建各个模块的对象
        for module_info in module_info_list:
            self.reg_module_info(module_info)
            self.reg_host_in_module(module_info)
        #初始化所有测试机
        self.init_hosts()
        #实例化模块对象
        self.instantiate_modules()


        #解析拓扑信息
        topology_info_list = self.conf.parse_topology()
        #自动创建关联关系
        for topology_info in topology_info_list:
            self._relate_module(topology_info)

        return 0

    def get_leaf(self, topology_list):
        """
        @author:    youguiyan01
        @note:      根据topo 获取 叶子节点
        @return     leaf:叶子节点list
                    如果出现循环，则leaf为[]
        """
        if topology_list == None:
            return []
        father = [one[0] for one in topology_list]
        child = [one[1] for one in topology_list]
        #除去父节点
        leaf = [ one for one in child if one not in father]
        leaf = list(set(leaf))
        return leaf


    def _set_remote_bash_profile(self,conf_ins):
        """
        @note:这个修改只在这一次的执行过程中有效，不会影响其他，但是如果想用这个path的话
              需要额外处理
              如果没有在topologicfile中设置该值的话，就不会设置环境变量
        @return:1 or 0
        """
        global_dict ={}
        for one_list in conf_ins._get_section("remote_bash_profile"):
            if one_list[0].endswith("_path"):
                apath = one_list[1]
                if apath.endswith('/'):
                    apath = apath[0:-1]
                if not os.path.isabs(apath):
                    apath = os.path.join(self.topology_file_dir , apath)
                global_dict.update({one_list[0]:apath})
            else:
                global_dict.update({one_list[0]:one_list[1]})
        self.init_global(global_dict)
        return 0



    def _relate_module(self,topology_info):
        """
        @author:    youguiyan01
        @note:      添加关联关系
        """
        up_module_name = topology_info[0]
        down_module_name = topology_info[1]
        return self.relate_module(up_module_name,down_module_name)


    def single_thread_run(self,method,modules=None):
        """
        @note:      串行的执行各个模块的method方法
        @return:    0：运行成功
                    1：运行失败
        """
        ret = 0
        if not modules:
            modules = [module["module"] for module in self.module_base]
        for module in modules:
            #执行method方法
            if method != None:
                #判断是否存在该方法
                if hasattr(module,method):
                    #执行该方法
                    if getattr(module,method)() != 0:
                       self.log.warning("run method error")
                       ret = 1
                else:
                    self.log.warning("no method in module")
                    ret = 1
            else:
                self.log.critical("you must give a method to Env for module running")
                ret = 1
        return ret

    def multi_thread_run(self,method,modules=None):
        """
        @note:      并行的执行各个模块的method方法
                    每个方法一个线程
                    注意！！！！
                    每个方法必须有返回值!!!!!!!
        @return:    0:  运行成功
                    1:  运行失败
        """
        all_func_list = []
        if not modules:
            modules = [module["module"] for module in self.module_base]
        for module in modules:
            func_dict = {}
            if method and hasattr(module,method):
                func_dict["func"]= getattr(module,method)
                #这里先不传参数，后续在说
                func_dict["args"] = None
                all_func_list.append(func_dict)
        run_thread = XDThread(all_func_list)
        run_thread.start()
        ret = run_thread.ret_value()
        return ret

    def has_up_module(self, topology_list, module_name):
        '''
        @note: 用于判断该节点是否有上游(入度不为0)
        @author: wangyue01
        '''
        count = 0
        for topo_relation in topology_list:
            if topo_relation[1] == module_name:
                count += 1

        if count == 0:
            return False
        else:
            return True

    def start_by_topology(self, start_method_name="start"):
        """
        @note: 根据topology配置关系并行分层启动模块，包括不在topology里的独立模块
        @author: wangyue01
        """
        # 计算出不在topology里配置的独立模块
        all_base_modules = [module_info["instance_name"] for module_info in self.module_base]
        topology_list = deepcopy((self.topo_info))
        all_topo_modules = []

        for topo_relation in topology_list:
            all_topo_modules.append(topo_relation[0])
            all_topo_modules.append(topo_relation[1])

        individual_modules = list(set(all_base_modules) - set(all_topo_modules))

        ret = 0
        while len(topology_list) > 0 or len(individual_modules) > 0:
            individual_modules = list(set(individual_modules))
            # 求出当前拓扑图的叶子节点列表
            leaf_module_list = self.get_leaf(topology_list)
            leaf_module_list.extend(individual_modules)

            # 保存本次被启动的节点列表
            if len(leaf_module_list) > 0:
                self.module_start_seq.append(leaf_module_list)

            leaf_modules = []
            for module_name in leaf_module_list:
                leaf_modules.append(self.get_module_by_instance_name(module_name))

            # 并行化启动叶子层，缩小等待时间
            ret += self.multi_thread_run(start_method_name, leaf_modules)
            if ret > 0:
                return 1

            # 移除叶子关系得到拓扑子图,对于入度为0的节点要加入individual_modules,否则会丢失拓扑关系
            individual_modules = []
            for topo_relation in topology_list[::-1]:
                if topo_relation[1] in leaf_module_list:
                    if not self.has_up_module(topology_list, topo_relation[0]):
                        individual_modules.append(topo_relation[0])

                    topology_list.remove(topo_relation)

        return 0

    def stop_by_topology(self, stop_method_name="stop"):
        """
        @note: 根据start_by_topology()提供相应的拓扑stop方法
                            注：如果用户启动时没有调用start_by_topology(), 则不应使用该方法来停止模块
        @author: wangyue01
        """
        ret = 0
        for started_module_list in self.module_start_seq[::-1]:
            if len(started_module_list) > 0:
                started_modules = []
                for module_name in started_module_list:
                    started_modules.append(self.get_module_by_instance_name(module_name))

                ret += self.multi_thread_run(stop_method_name, started_modules)

                if ret > 0:
                    return 1
        return 0

class XDThread(object):
    """
    @note:  多个函数，每个函数一个线程来执行
            由于threading模块未提供线程函数返回结果获取接口
            封装多线程模块，支持各个线程函数的返回值检查，来确定最终环境搭建的成功与否
            检查函数返回0认为成功
    """

    def __init__(self, func_list=None):
        """
        @note:  初始化一些需要的值
        """
        #所有函数的返回值之和，如果有函数执行失败，则ret_flag不等于0
        self.ret_flag = 0
        #需要执行的函数列表
        self.func_list = func_list
        #线程列表
        self.threads = []

    def set_thread_func_list(self, func_list):
        """
        @note: func_list是一个list，每个元素是一个dict，有func和args两个参数
        """
        self.func_list = func_list

    def __trace_func(self, func, *args, **kwargs):
        """
        @note:  跟踪线程返回值的函数，对真正执行的线程函数包一次函数，以获取返回值
        """
        ret = func(*args, **kwargs)
        #收集返回值
        self.ret_flag += ret

    def start(self):
        """
        @note: 启动多线程执行，并阻塞到结束
        """
        import threading
        self.threads = []
        self.ret_flag = 0
        for func in self.func_list:
            args = []
            #添加函数名称
            args.append(func["func"])
            if func["args"] != None:
                #添加函数参数
                args += func["args"]
            args_tuple = tuple(args)
            t = threading.Thread(target=self.__trace_func, args=args_tuple)
            self.threads.append(t)
        #启动线程
        for thread_obj in self.threads:
            thread_obj.start()
        #等待线程
        for thread_obj in self.threads:
            thread_obj.join()

    def ret_value(self):
        """
        @note: 所有线程函数的返回值之和，如果为0那么表示左右函数执行成功
        """
        return self.ret_flag

