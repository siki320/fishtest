# -*- coding: GB18030 -*-
"""
@author: duquanxi
@modified:
@date: Mar 3 10:49:31 CST 2012
@summary: mysql deploy
@version: 1.0.0.0
@copyright: Copyright (c) 2012 XX, Inc. All Rights Reserved
"""

from frame.lib.deploylib.basemodule import BaseModule
import os


class Mysql(BaseModule):
    """
    @note: mysql deploy,使用示例请参考 demo/deploy_demo_mysql
    """
    def __init__(self, host="127.0.0.1", user="work", local_path="/home/work/mysql", \
                 instance_name=None,passwd="shifenqa", config_file = None, mysql_conf = "etc/my.cnf"):
        """
        @note: init
        @param host: 机器ip
        @param local_path: 安装位置
        @param instance_name：通过Env取对像时需要，默认与type相等，Env中应保持独立
        @param config_file: 用于指定mysql下载安装包的文件
        @param mysql_conf: 此参数为指定mysql的cnf所在位置，如果全新安装，此参数不起指定做用，将默认安装在etc/my.cnf中
        """
        BaseModule.__init__(self, host, user, local_path, instance_name, passwd, config_file = config_file)
        self.install_path = os.path.realpath(local_path)
        self.local_path = self.install_path
        #默认端口
        self.listen_port=3306
        #设置本模块type
        self.type = "mysql"
        self.mysql_conf = mysql_conf

    def system(self, cmd, message = "message"):
        self.log.info("shell cmd: %s" %(cmd))
        if self.sys.xd_system(cmd) != 0:
            raise Exception("%s; CMD:%s" %(message, cmd))

    def getTarFile(self):
        tarfile = None
        for file in os.listdir(self.local_path):
            if file.endswith(".tar.gz"):
                tarfile = file
                break
        if tarfile:
            return tarfile[0:len(tarfile)-7] , tarfile
        return None, None

    def preprocess(self):
        unzipfolder, tarfile = self.getTarFile()
        #如果存在，认为mysql已安装
        if os.path.exists(self.install_path + "/" + "/bin"):
            self.warning("mysql has been installed")
            return 0

        #执行安装脚本解压文件
        thiPyFilePath = os.path.dirname(os.path.realpath(__file__))
        cmd = "sh -x %s/install_mysql.sh %s %s %s %s" %(thiPyFilePath, self.install_path, self.local_path, tarfile, unzipfolder )
        self.system(cmd, "install mysql error")
        return 0


    def set_listen_port(self):
        #Dtest-deploy端口自适应分配给本模块的端口列表存放于self.port_list中
        port = self.port_list[0]
        self.listen_port = self.__get_conf_port()
        cmd = "sed -i 's/%d/%d/g' %s" %(self.listen_port, port, self.install_path + "/" + self.mysql_conf)
        self.system(cmd, "set mysql port error")
        self.listen_port = port

        self.log.warning("write conf here to set listen port")
        self.log.warning("bs listen port is %s" % self.listen_port)

    def get_listen_port(self):
        self.listen_port = self.__get_conf_port()
        return self.host_info["host"], self.listen_port

    def __get_conf_port(self):
        cmd = "grep -E \"^port.*=.*[0-9]*\" %s" %(self.install_path + "/" + self.mysql_conf)
        grep_line = os.popen(cmd).readlines()[0]
        return int(grep_line.split('=')[1])

    def start(self):
        cmd = "cd %s && ./mysql.server start" %(self.install_path)
        self.system(cmd, "start mysql error")
        return 0

    def restart(self):
        cmd = "cd %s && ./mysql.server restart" %(self.install_path)
        self.system(cmd, "restart mysql error")
        return 0

    def stop(self):
        cmd = "cd %s && ./mysql.server stop" %(self.install_path)
        self.system(cmd, "stop mysql error")
        return 0

    def add_read_user(self, user="read", passwd="123456"):
        """
        @note: 添加只读帐户，使用者需先通过Env拿到Mysql的对象
        @param user: 用户名
        @param passwd: 密码
        """
        self.add_user(user, passwd, "SELECT")

    def add_write_user(self, user="write", passwd="123456"):
        """
        @note: 添加写帐户，使用者需先通过Env拿到Mysql的对象
        @param user: 用户名
        @param passwd: 密码
        """
        self.add_user(user, passwd, "DELETE,INSERT,UPDATE,SELECT")

    def add_user(self, user, passwd, privalige):
        sql = "GRANT %s ON *.* to '%s'@'%%' identified by '%s'" %(privalige, user, passwd)
        cmd = 'cd %s && ./bin/mysql -uroot -P%d -e "%s"' %(self.install_path, self.listen_port, sql)
        self.system(cmd, "add user fail")
        sql = "GRANT %s ON *.* to '%s'@'localhost' identified by '%s'" %(privalige, user, passwd)
        cmd = 'cd %s && ./bin/mysql -uroot -P%d -e "%s" '  %(self.install_path, self.listen_port, sql)
        self.system(cmd, "add user fail")

    def query(self, sql = "show tables"):
        """
        @note: 使用root权限执行sql语句
        @param sql: 执行的sql语句
        @return: 结果行list
        """
        cmd = "cd %s && ./bin/mysql -uroot -e '%s'" %(self.install_path, sql)
        return os.popen("cmd").readlines()

    def mysqlimport(self, ext_cmd="--default-character-set=gbk", import_file="./temp_dump.file"):
        """
        @note: 用于数据import，数据来源应为使用mysqldump工具导出的数据文件，和mysql中执行source 命令方法相同
        @param ext_cmd: 执行mysql命令时的扩展参数，如“FC_Word”，表明向FC_Word库中导入数据
        @param import_file: 导入的文件
        """
        cmd = "cd %s && ./bin/mysql -uroot -P%d %s <%s" %(self.install_path, self.listen_port, ext_cmd, import_file)
        self.system(cmd, "import error")

    def mysqldump(self, remote_host ,remote_port, remote_user, remote_pass, \
           ext_cmd="--add-drop-table --add-drop-database --default-character-set=gbk --all-databases --lock-tables=0", \
           dump_file = "./temp_dump.file"):
        """
        @note: 用于从远端db导出数据，远端db需可访问
        @param remote_host, remote_user, remote_pass: 远端ip, user, password
        @param ext_cmd: mysqldump工具的扩展命令
        @param dump_file: 导出文件的位置
        """
        cmd = "cd %s && ./bin/mysqldump -h%s -P%d -u%s -p%s %s > %s" \
                  %(self.install_path, remote_host, remote_port, remote_user, remote_pass, ext_cmd, dump_file)
        self.system(cmd, "dump error")
        return dump_file

