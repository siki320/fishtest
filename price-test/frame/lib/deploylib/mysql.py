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
    @note: mysql deploy,ʹ��ʾ����ο� demo/deploy_demo_mysql
    """
    def __init__(self, host="127.0.0.1", user="work", local_path="/home/work/mysql", \
                 instance_name=None,passwd="shifenqa", config_file = None, mysql_conf = "etc/my.cnf"):
        """
        @note: init
        @param host: ����ip
        @param local_path: ��װλ��
        @param instance_name��ͨ��Envȡ����ʱ��Ҫ��Ĭ����type��ȣ�Env��Ӧ���ֶ���
        @param config_file: ����ָ��mysql���ذ�װ�����ļ�
        @param mysql_conf: �˲���Ϊָ��mysql��cnf����λ�ã����ȫ�°�װ���˲�������ָ�����ã���Ĭ�ϰ�װ��etc/my.cnf��
        """
        BaseModule.__init__(self, host, user, local_path, instance_name, passwd, config_file = config_file)
        self.install_path = os.path.realpath(local_path)
        self.local_path = self.install_path
        #Ĭ�϶˿�
        self.listen_port=3306
        #���ñ�ģ��type
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
        #������ڣ���Ϊmysql�Ѱ�װ
        if os.path.exists(self.install_path + "/" + "/bin"):
            self.warning("mysql has been installed")
            return 0

        #ִ�а�װ�ű���ѹ�ļ�
        thiPyFilePath = os.path.dirname(os.path.realpath(__file__))
        cmd = "sh -x %s/install_mysql.sh %s %s %s %s" %(thiPyFilePath, self.install_path, self.local_path, tarfile, unzipfolder )
        self.system(cmd, "install mysql error")
        return 0


    def set_listen_port(self):
        #Dtest-deploy�˿�����Ӧ�������ģ��Ķ˿��б�����self.port_list��
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
        @note: ���ֻ���ʻ���ʹ��������ͨ��Env�õ�Mysql�Ķ���
        @param user: �û���
        @param passwd: ����
        """
        self.add_user(user, passwd, "SELECT")

    def add_write_user(self, user="write", passwd="123456"):
        """
        @note: ���д�ʻ���ʹ��������ͨ��Env�õ�Mysql�Ķ���
        @param user: �û���
        @param passwd: ����
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
        @note: ʹ��rootȨ��ִ��sql���
        @param sql: ִ�е�sql���
        @return: �����list
        """
        cmd = "cd %s && ./bin/mysql -uroot -e '%s'" %(self.install_path, sql)
        return os.popen("cmd").readlines()

    def mysqlimport(self, ext_cmd="--default-character-set=gbk", import_file="./temp_dump.file"):
        """
        @note: ��������import��������ԴӦΪʹ��mysqldump���ߵ����������ļ�����mysql��ִ��source �������ͬ
        @param ext_cmd: ִ��mysql����ʱ����չ�������硰FC_Word����������FC_Word���е�������
        @param import_file: ������ļ�
        """
        cmd = "cd %s && ./bin/mysql -uroot -P%d %s <%s" %(self.install_path, self.listen_port, ext_cmd, import_file)
        self.system(cmd, "import error")

    def mysqldump(self, remote_host ,remote_port, remote_user, remote_pass, \
           ext_cmd="--add-drop-table --add-drop-database --default-character-set=gbk --all-databases --lock-tables=0", \
           dump_file = "./temp_dump.file"):
        """
        @note: ���ڴ�Զ��db�������ݣ�Զ��db��ɷ���
        @param remote_host, remote_user, remote_pass: Զ��ip, user, password
        @param ext_cmd: mysqldump���ߵ���չ����
        @param dump_file: �����ļ���λ��
        """
        cmd = "cd %s && ./bin/mysqldump -h%s -P%d -u%s -p%s %s > %s" \
                  %(self.install_path, remote_host, remote_port, remote_user, remote_pass, ext_cmd, dump_file)
        self.system(cmd, "dump error")
        return dump_file

