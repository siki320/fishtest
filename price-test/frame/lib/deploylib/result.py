# -*- coding: GB18030 -*-
"""
@author: guoan
@modify: geshijing
@date: Jun 19, 2012
@summary: result描述类 ,用于dtsdeploy的数据收集,提供提交到dts-deploy dashboad接口
@version: 1.0.0.0
@copyright: Copyright (c) 2011 XX, Inc. All Rights Reserved
"""
from frame.tools.lib.mysqldb import MySQLdb
import time

DB_HOST = "10.237.2.72"
DB_USER = "root"
DB_PORT = 3606
DB_PASSWD = "MhxzKhl"

class Env_result(object):
    def __init__(self,**args):
        self.app_name = None
        self.app_file = None
        self.app_type = None
        self.product_name = None
        self.start_time = None
        self.deploy_time = None
        self.modules_num = 0
        #包含各个module的result情况
        self.module_result_list = []
        self.__dbname = 'dts_deploy_info_stat'

    def clear_module_info(self):
        self.module_result_list = []
        self.modules_num = 0

    def collect_module_result(self,result):
        """
        @note: 收集各个模块的搭建信息记录
        """
        self.module_result_list.append(result)
        self.modules_num += 1
        return 0

    def set_deploy_time(self,s_time,d_time):
        """
        @note:set download time
        @param s_time: start time for this module download
        @param d_time: delta time for this module download
        """
        self.start_time = s_time
        self.deploy_time = d_time
        return 0

    def set_product_name(self,product_name):
        self.product_name = product_name

    def set_app_name(self,app_name):
        self.app_name = app_name

    def set_app_file(self,app_file):
        self.app_file = app_file

    def set_app_type(self,app_type):
        self.app_type = app_type

    def set_env_info(self,product_name,app_name,app_file,app_type='NULL'):
        """
        @note:set product and app names
        @param product: product name
        @param app: app name
        """
        self.set_product_name(product_name)
        self.set_app_name(app_name)
        self.set_app_file(app_file)
        self.set_app_type(app_type)
        return 0

    def print_result_info(self):
        """
        @note:just for debug!!!
        """
        print "app_name:"+self.app_name
        print "product_name:"+self.product_name
        print "env start_time:"+ str(self.start_time)
        print "env deploy_time:"+ str(self.deploy_time)
        for one_module in self.module_result_list:
            print "type:"+one_module.type
            print "path:"+one_module.path
            print "host:"+one_module.host
            print "user:"+one_module.user
            print "instance_name:"+one_module.instance_name
            print "delta_time:"+str(one_module.delta_time)
            print "start_time:"+str(one_module.start_time)
            print "module_rel_set:"+one_module.module_rel_set
            print "element_dict is :"
            print one_module.element_dict

    def dump_to_db(self):
        conn = MySQLdb.connect(host=DB_HOST,user=DB_USER, port=DB_PORT, passwd=DB_PASSWD, db=self.__dbname)
        cursor=conn.cursor()
        #插入app recode 的sql
        insert_app = 'INSERT into app_info(product_line,app_name,app_file,app_type,start_time,deploy_time,cur_timestamp) VALUES("%s","%s","%s","%s","%s","%s","%s" )'\
            %(self.product_name,self.app_name,self.app_file,self.app_type,str(self.start_time),str(self.deploy_time),time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
        cursor.execute(insert_app)
        #获取插入的app_id
        app_id  =  int(conn.insert_id())
        for one_module in self.module_result_list:
            insert_module = 'INSERT into module_info(app_id,module_name,instance_name,host_name,path,user,delta_time,start_time,cur_timestamp) VALUES("%d","%s","%s","%s","%s","%s","%s","%s","%s")'\
                %(app_id,one_module.type,one_module.instance_name,one_module.host,one_module.path,one_module.user,str(one_module.delta_time),str(one_module.start_time),time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
            cursor.execute(insert_module)
        for one_module in self.module_result_list:
            for rel_instance in one_module.topo_down:
                insert_topo = 'INSERT into topo_info(app_id,instance,related) VALUES("%d","%s","%s")'\
                    %(app_id,one_module.instance_name,rel_instance)
                cursor.execute(insert_topo)
        conn.commit()
        cursor.close()
        conn.close()

class Module_Result(object):
    def __init__(self,**args):
        """
        @note:针对模块级别，基本的信息收集器
        """
        self.type = args["type"]
        self.path = args["path"]
        self.host = args["host"]
        self.user = args["user"]
        self.instance_name = args["instance"]
        self.delta_time = None
        self.start_time = None
        self.module_rel_set = ""
        self.topo_down =[]
        self.app_name = None
        self.product_name = None
        #you can get all info from here
        self.element_dict = {}

    def set_download_time(self,s_time,d_time):
        """
        @note:set download time
        @param s_time: start time for this module download
        @param d_time: delta time for this module download
        """
        self.start_time = s_time
        self.delta_time = d_time
        return 0

    def set_module_rel_set(self,module_rel_set):
        """
        @note:set module_rel_set for topologic
        @param module_rel_set: module_rel_set
        """
        self.module_rel_set = ""
        if len(module_rel_set) <> 0:
            for one_module in module_rel_set:
                #添加链表以供dash_board使用
                self.topo_down.append(one_module.instance_name)
                self.module_rel_set += "-%s-"%(one_module.instance_name)
        else:
            self.module_rel_set = "null"
        return 0

    def set_product_name(self,product_name):
        self.product_name = product_name

    def set_app_name(self,app_name):
        self.app_name = app_name

    def set_module_info(self,product_name,app_name):
        """
        @note:set product and app names
        @param product: product name
        @param app: app name
        """
        self.set_product_name(product_name)
        self.set_app_name(app_name)
        return 0

'''
class DBProxy(object):
    def __init__(self, host, port, user, passwd):
        self.host = host
        self.user = user
        self.port = port
        self.passwd = passwd
        self.__dbname = 'dts_deploy_info_stat'

    def init_database(self):
        conn = MySQLdb.connect(host=self.host,user=self.user, port=self.port, passwd=self.passwd, db=self.__dbname)
        cursor=conn.cursor()
        cursor.execute("create TABLE app_info (app_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, product_line VARCHAR(100),app_name VARCHAR(100), app_type VARCHAR(100),start_time VARCHAR(50), deploy_time VARCHAR(50) ,cur_timestamp TIMESTAMP)")
        cursor.execute("create TABLE module_info (app_id INT NOT NULL,FOREIGN KEY (app_id) REFERENCES app_info(app_id) , module_name VARCHAR(100), instance_name VARCHAR(50), host_name VARCHAR(100),path VARCHAR(100),user VARCHAR(100),delta_time VARCHAR(100),start_time VARCHAR(100),cur_timestamp TIMESTAMP)")
        cursor.execute("create TABLE topo_info (app_id INT NOT NULL,FOREIGN KEY (app_id) REFERENCES app_info(app_id), instance VARCHAR(50),related VARCHAR(50),reserved VARCHAR(100))")
        cursor.close()
        conn.close()

if __name__=="__main__":
    de_proxy = DBProxy(DB_HOST,DB_PORT,DB_USER,DB_PASSWD)
    de_proxy.init_database()
'''
