# -*- coding: GB18030 -*-
"""
@author: songyang
@modify: youguiyan01
@modify: maqi
@modify: xuwei01
@summary: ���𻷾����ͳһ����
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
    @note: ���𻷾���ͳһ���ȣ���������ģ��Ĵ������������ϵ���˿�����Ӧ��
    """
    def __init__(self,log=dlog,auto_dispatch=False,auto_module_path=False):
        """
        @note: ������Ϣ�ĳ�ʼ������Ҫ�Ǳ���������
        """
        #���ģ�����ϸ��Ϣ������ģ������ģ�����ڵ�host��user, path����ģ������
        self.module_base = []
        self.log = log
        self.sys = XDSystem(self.log)
        self.conf = None
        self.topology_file = None
        self.topology_file_dir = None
        self.is_inited = False
        self.init_dashboard = False
        self.bash_profile_list=[]
        #env�ռ���Ϣ��������
        self.env_result = Env_result()

        # ģ������˳���б������ڰ���������/�ر�ģ��
        self.module_start_seq = []

        self.host_dict = {}
        self.module_host_require = {}
        self.atd_jobid = None
        self.module_info_dict = {}
        self.topo_info = []

        # ����python path���ļ��е�����
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

        #ʹ��xstp�������
        self.is_xstp = False
        self.xstp_host_info_list = []

    def init_global(self,global_dict):
        '''
        @author:    geshijing
        @note:
            ��ʼ��������Ҫʹ�õĻ���������Ҫ������������
            #xds_framelib_path: dts frame path
            #xds_modulelib_path:dts module path
            #xds_force_dispatch:true or false �����Ƿ�ַ����룬Ĭ��ǿ�Ʒַ�
            #xds_force_rpyc_start:ture or False �����Ƿ�����Զ��rpyc����Ĭ��ǿ������
            #which_to_dispatch:��������xds_framelib_path��֮���Կո����������֧�ֶ�·������
            #����ʹ�õ����·�����������app �ļ����ڵ�Ŀ¼
            #������topy �ļ�ʹ�õ����·����һ����topy�ļ���ʹ�õ����·��������� topy �ļ������
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
            ע�������Ϣ
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
            �Զ���������������Ľӿڣ���ģ���ֵ��л�ȡ��Ҫ�Ļ�����Ϣ
            ��ӵĻ�����Ϣ����init_hosts���������
        '''
        if module_info["host_name"] !="ATD_AUTO":
            return
        name = module_info["module_name"]
        #atd�����·������ȥ��ʱû����
        cpucore_require = int(module_info.get("cpuCoreNum",'0'))
        mem_require = int(module_info.get("mem",'0'))
        disk_require = int(module_info.get("disk",'0'))
        #��ʹ��atd����Ķ˿�
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
        @note�� ������Ի�
        '''
        return

    def add_host(self,host_name,user_name,password):
        '''
        @author:geshijing
        @note:ע�Ტ�ҳ�ʼ��һ���µĲ��Ի�
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
            �������
            ��ʼ����������
            ��Ҫ���ݣ�
            �������ι�ϵ
            �ַ����������
            ����RPYC
        '''
        #����atd�ӿ��������
        self._acquire_hosts()
        #��ʼ�����еĲ��Ի�
        for host in self.host_dict:
            self.host_dict[host].set_log_sys(self.log,self.sys)
            self.host_dict[host].build_xds_client()


    def release_atd_resource(self):
        '''
        @author: geshijing@XX
        @note:
            �ͷ��Ѿ�����Ļ���
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
            ǰ���й��ޣ�С��ʹ��
            ɾ�������е�һ��ģ��
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
        @note: ע��ģ����Ϣ���Ա��������ʵ����ģ��
        @param module_info: ģ����Ϣ�ֵ�
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
        @note:      ʵ����ģ�����Զ�̵Ķ���ʹ��RPYCʵ����������ʵ����֮ǰ��Ҫ����reg_module_infoע��ģ����Ϣ
        @param module_info: ģ����Ϣ
        '''
        #��Ҫע���ģ��������bdbs1
        module_name  = module_info["module_name"]
        class_name = module_info["class_name"]

        #��Ҫ�����ģ��,����Novabsӳ�䵽nova_bs.Novabs����ô��Ҫfrom nova_bs import Novabs
        from_module = ".".join(self.module_name_dict[class_name].split(".")[0:-1])
        import_module = self.module_name_dict[class_name].split(".")[-1]
        #sys.path.append(os.path.expanduser("~/.XDS_CLIENT"))

        tmpmod = __import__(from_module,globals(),locals(),[import_module],-1)

        #��������,�����б������Ƕ�̬��
        setattr(self,module_name,getattr(tmpmod,import_module)(instance_name=module_name,config_file=module_info["conf_file"],local_path=module_info["remote_path"],
                host=module_info["host_name"],user=module_info["user"],passwd=module_info["password"]))
        #ע�����
        self._register_module(getattr(self,module_name))

    def instantiate_modules(self):
        '''
        @author:    geshijing
        @note:      ����ʵ����ģ����󣬵���instantiate_module����
        '''
        for module in self.module_info_dict:
            self.instantiate_module(self.module_info_dict[module])


    def relate_module(self,module_upstream,module_downstream):
        """
        @author:    youguiyan01
        @note:      ��ӹ�����ϵ
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
        @note:      ɾ��������ϵ
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
        @note:      ����ģ���ֵ�
            ����������ǰ��Ҫ��app��д��,���������ǾͿ���ֱ��ʹ��Novabs
            from novalib.bs.bs import Novabs
            ��ô��������ֻ��Ҫд��
            key:�����������Novabs
            value:���������ڵľ���λ��(�����ļ�·��),novalib.bs.bs.Novabs
            �Ϳ�����
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
        @note:App�����ڴ�����ģ�����
        """
        pass


    def _register_modules(self):
        """
        @note:�Զ�ע��ģ��
        """
        for item in dir(self):
            attr = getattr(self, item)
            if isinstance(attr,BaseModule):
                self._register_module(attr)

    def _register_module_info(self,module_info):
        '''
        @note: ʹ��reg_module_info��instantiate_moduleע�Ტ��ʵ����һ��ģ��
        '''
        self.reg_module_info(module_info)
        self.instantiate_module(module_info)

    def _register_module(self,module):
        """
        @note:      ע����Ҫ���ģ������Log����
        @param:     module:ģ�����
                    log:��־����
        @return:    0:�ɹ�
                    1:ʧ��
        """
        #ÿһ�����󶼽���handlers�ĳ�ʼ��
        if hasattr(module,"init_handlers") and getattr(module, "init_handlers")(self.log) != 0:
            self.log.critical("init_handlers error!")
            return 1

        #��ģ�����ϸ��Ϣ��ӵ��б���
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
        @note:     ����instance_name����þ����module����ע��instance_name�ĸ�ֵ�߼��������ģ�
                   1.����init module��instance_name�������ø�ֵ
                   2.���û�и�instance_name��ֵ�Ļ���Ĭ��ʹ��type��Ϊinstance_name
        @param     instance_name: ģ��ʵ������ÿ��moduleΨһ
        @return:   module \ ���û���ҵ��Ļ����ؿ�
        """
        for module_info in self.module_base:
            if (module_info["instance_name"] == instance_name ):
                return module_info["module"]
            else:
                continue
        return

    def _port_adaptive(self,start_port = 61000):
        """
        @note: �˿�����Ӧ,�ֳ��������ռ�ռ�ö˿ڣ�������ö˿ڣ�������ö˿�
        """
        for module_dict in self.module_base:
            getattr(module_dict["module"],"port_adaptive")()
            getattr(module_dict["module"],"set_listen_port")()
            self.log.info("set %s port : %s" ,str(getattr(module_dict["module"],"type")) \
                    ,str(getattr(module_dict["module"],"get_listen_port")()))
        return 0


    def update(self,module_list):
        """
        @note: �ֲ�����,�ؽ��ֲ����ӹ�ϵ
        module_list:���Ĺ���ģ���б�
        """
        if not isinstance(module_list,list):
            module_list = [module_list]

        #��ȡ����Ӱ�������ģ��
        all_affected_modules = self._get_affected_modules(module_list)

        #�ؽ�ģ�����ӹ�ϵ
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
        @note: ��ȡ����Ӱ�쵽������ģ��
        '''
        all_affected_modules = []
        for module_dict in self.module_base:
            module_rel_set = module_dict["module"].module_rel_set
            if set(module_rel_set) & set(module_list):
                all_affected_modules.append(module_dict["module"])
        return all_affected_modules

    def get_app_filename(self):
        """
        @note: ��ȡ��ǰapp��ִ���ļ���,��ȡ���ȵ�������ļ���
        """
        stack =traceback.extract_stack()
        if len(stack) >=2:
            func = stack[0][0]
        return func

    def get_type_name(self):
        '''
        @note: ��ȡ��ǰ��app��������
        '''
        return "%s.%s"%(type(self).__module__,type(self).__name__)

    def set_attr_for_dashboard(self,product="ecom",appname='defaultapp'):
        """
        @note: ������sql��������Ŀ���
               ����app\product������
        """
        self.env_result.set_env_info(product,appname,self.get_app_filename(),self.get_type_name())
        self.init_dashboard = True

    def collect_module_results(self):
        """
        @note: �ռ�������ģ������н��
        """
        #������е�ģ����¼
        self.env_result.clear_module_info()
        for module_info in self.module_base:
            self.env_result.collect_module_result(module_info["module"].result_obj)

    def save_result_to_sql(self):
        """
        @note: 1��save one record for this app
               2��save many records for modules
               3��save topo info for this app
        """
        try:
            self.env_result.dump_to_db()
        except:
            print "mysql server is downing ,please wait for a moment!!!"

    def init_env(self):
        """
        @note:�������������ԭ��������ɾ��element����Ҫ
              �����Ҫʹ��del_element���������ȵ��øú���
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
        @note:�Ѿ���̭�Ľӿڣ���ֱ��ʹ��deploy
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
        #���̵߳���ģ��ı��ݷ���
        self.multi_thread_run("backup")

    def dump(self,filepath):
        '''
        �������л�
        '''
        fd = file(filepath, 'wb')
        pickle.dump(self,fd,True)
        fd.close()

    def set_topology_file(self, file=''):
        '''
        @note: ���ô������ȡ���˹�ϵ���ļ�
        '''
        if False == os.path.exists(file):
            self.log.critical("Input invalid filename: %s" % file)
            return 1

        self.topology_file = os.path.basename(file)
        self.topology_file_dir = get_abs_dir(os.path.dirname(file)) + '/'

        return 0

    def set_hostinfo_file(self, hfile=''):
        '''
        @note: ���ô������ȡxstp����Ļ�����Ϣ
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
        @note: �������������ļ�
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
        #����ģ�鲢ע��
        self._register_modules()
        if self.conf is None:
            return 0
        #����������ϵ
        topology_info_list = self.conf.parse_topology()
        for topology_info in topology_info_list:
            self._relate_module(topology_info)
        return 0

    def _parse_topology_mm(self):
        """
        @author:youguiyan01
        @param  topology_file:���˽ṹ�ļ�
        @note:  �������˽ṹ���������˽ṹ��������Ӧ�Ķ��󣬲�����������ϵ
        """
        #��ȡԶ�̴��Ҫ�Ļ���������Ϣ
        self._set_remote_bash_profile(self.conf)
        #����module name dict ��Ϣ
        if self.conf.get_conf_version() == "3":
            module_name = self.conf.parse_module_name_dict()
            if module_name != None:
                self.module_name_dict = module_name
        #����ģ����Ϣ
        host_info_list,module_info_list = self.conf.parse_host_module()

        if host_info_list == None:
            return 1

        for host_info in host_info_list:
            self.reg_host_info(host_info["host_name"].strip(),host_info["user"],host_info["password"])
        #����xstp���»����б�,��ģ����Ϣ
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

        #�Զ���������ģ��Ķ���
        for module_info in module_info_list:
            self.reg_module_info(module_info)
            self.reg_host_in_module(module_info)
        #��ʼ�����в��Ի�
        self.init_hosts()
        #ʵ����ģ�����
        self.instantiate_modules()


        #����������Ϣ
        topology_info_list = self.conf.parse_topology()
        #�Զ�����������ϵ
        for topology_info in topology_info_list:
            self._relate_module(topology_info)

        return 0

    def get_leaf(self, topology_list):
        """
        @author:    youguiyan01
        @note:      ����topo ��ȡ Ҷ�ӽڵ�
        @return     leaf:Ҷ�ӽڵ�list
                    �������ѭ������leafΪ[]
        """
        if topology_list == None:
            return []
        father = [one[0] for one in topology_list]
        child = [one[1] for one in topology_list]
        #��ȥ���ڵ�
        leaf = [ one for one in child if one not in father]
        leaf = list(set(leaf))
        return leaf


    def _set_remote_bash_profile(self,conf_ins):
        """
        @note:����޸�ֻ����һ�ε�ִ�й�������Ч������Ӱ����������������������path�Ļ�
              ��Ҫ���⴦��
              ���û����topologicfile�����ø�ֵ�Ļ����Ͳ������û�������
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
        @note:      ��ӹ�����ϵ
        """
        up_module_name = topology_info[0]
        down_module_name = topology_info[1]
        return self.relate_module(up_module_name,down_module_name)


    def single_thread_run(self,method,modules=None):
        """
        @note:      ���е�ִ�и���ģ���method����
        @return:    0�����гɹ�
                    1������ʧ��
        """
        ret = 0
        if not modules:
            modules = [module["module"] for module in self.module_base]
        for module in modules:
            #ִ��method����
            if method != None:
                #�ж��Ƿ���ڸ÷���
                if hasattr(module,method):
                    #ִ�и÷���
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
        @note:      ���е�ִ�и���ģ���method����
                    ÿ������һ���߳�
                    ע�⣡������
                    ÿ�����������з���ֵ!!!!!!!
        @return:    0:  ���гɹ�
                    1:  ����ʧ��
        """
        all_func_list = []
        if not modules:
            modules = [module["module"] for module in self.module_base]
        for module in modules:
            func_dict = {}
            if method and hasattr(module,method):
                func_dict["func"]= getattr(module,method)
                #�����Ȳ���������������˵
                func_dict["args"] = None
                all_func_list.append(func_dict)
        run_thread = XDThread(all_func_list)
        run_thread.start()
        ret = run_thread.ret_value()
        return ret

    def has_up_module(self, topology_list, module_name):
        '''
        @note: �����жϸýڵ��Ƿ�������(��Ȳ�Ϊ0)
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
        @note: ����topology���ù�ϵ���зֲ�����ģ�飬��������topology��Ķ���ģ��
        @author: wangyue01
        """
        # ���������topology�����õĶ���ģ��
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
            # �����ǰ����ͼ��Ҷ�ӽڵ��б�
            leaf_module_list = self.get_leaf(topology_list)
            leaf_module_list.extend(individual_modules)

            # ���汾�α������Ľڵ��б�
            if len(leaf_module_list) > 0:
                self.module_start_seq.append(leaf_module_list)

            leaf_modules = []
            for module_name in leaf_module_list:
                leaf_modules.append(self.get_module_by_instance_name(module_name))

            # ���л�����Ҷ�Ӳ㣬��С�ȴ�ʱ��
            ret += self.multi_thread_run(start_method_name, leaf_modules)
            if ret > 0:
                return 1

            # �Ƴ�Ҷ�ӹ�ϵ�õ�������ͼ,�������Ϊ0�Ľڵ�Ҫ����individual_modules,����ᶪʧ���˹�ϵ
            individual_modules = []
            for topo_relation in topology_list[::-1]:
                if topo_relation[1] in leaf_module_list:
                    if not self.has_up_module(topology_list, topo_relation[0]):
                        individual_modules.append(topo_relation[0])

                    topology_list.remove(topo_relation)

        return 0

    def stop_by_topology(self, stop_method_name="stop"):
        """
        @note: ����start_by_topology()�ṩ��Ӧ������stop����
                            ע������û�����ʱû�е���start_by_topology(), ��Ӧʹ�ø÷�����ֹͣģ��
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
    @note:  ���������ÿ������һ���߳���ִ��
            ����threadingģ��δ�ṩ�̺߳������ؽ����ȡ�ӿ�
            ��װ���߳�ģ�飬֧�ָ����̺߳����ķ���ֵ��飬��ȷ�����ջ�����ĳɹ����
            ��麯������0��Ϊ�ɹ�
    """

    def __init__(self, func_list=None):
        """
        @note:  ��ʼ��һЩ��Ҫ��ֵ
        """
        #���к����ķ���ֵ֮�ͣ�����к���ִ��ʧ�ܣ���ret_flag������0
        self.ret_flag = 0
        #��Ҫִ�еĺ����б�
        self.func_list = func_list
        #�߳��б�
        self.threads = []

    def set_thread_func_list(self, func_list):
        """
        @note: func_list��һ��list��ÿ��Ԫ����һ��dict����func��args��������
        """
        self.func_list = func_list

    def __trace_func(self, func, *args, **kwargs):
        """
        @note:  �����̷߳���ֵ�ĺ�����������ִ�е��̺߳�����һ�κ������Ի�ȡ����ֵ
        """
        ret = func(*args, **kwargs)
        #�ռ�����ֵ
        self.ret_flag += ret

    def start(self):
        """
        @note: �������߳�ִ�У�������������
        """
        import threading
        self.threads = []
        self.ret_flag = 0
        for func in self.func_list:
            args = []
            #��Ӻ�������
            args.append(func["func"])
            if func["args"] != None:
                #��Ӻ�������
                args += func["args"]
            args_tuple = tuple(args)
            t = threading.Thread(target=self.__trace_func, args=args_tuple)
            self.threads.append(t)
        #�����߳�
        for thread_obj in self.threads:
            thread_obj.start()
        #�ȴ��߳�
        for thread_obj in self.threads:
            thread_obj.join()

    def ret_value(self):
        """
        @note: �����̺߳����ķ���ֵ֮�ͣ����Ϊ0��ô��ʾ���Һ���ִ�гɹ�
        """
        return self.ret_flag

