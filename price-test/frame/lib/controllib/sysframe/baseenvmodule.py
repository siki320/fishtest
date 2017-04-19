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

from frame.lib.deploylib.basemodule import BaseModule


class BaseEnvModule(BaseModule):
    def __init__(self,host="127.0.0.1", user="localuser", local_path="./",instance_name=None,passwd=None,**args):
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


    def init_handlers(self,log):
        #什么都不做，避免读取element相关信息
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
