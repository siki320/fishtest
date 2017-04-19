# -*- coding: GB18030 -*-
"""
@author: guoan
@date: Nov 29, 2011
@summary: element描述类
@version: 1.1.0.0
@copyright: Copyright (c) 2011 XX, Inc. All Rights Reserved
"""
class Element(object):
    def __init__(self,**args):
        """
        @note:downloadobj \ src_dict \ dst_dict都是在baseobj中初始化的
        我们对element可以做任何事情，因为我们其实有了element的信息
        @param args: 命名参数，目前只有name,file_path,downloader,src,dst,des可能被使用
        """
        self.name = args.get("name")
        self.file_path = args.get("file_path")
        self.downloadobj = args.get("downloader")
        self.src_dict = args.get("src")
        self.dst_dict = args.get("dst")
        self.des_data_dict = args.get("des")
        self.__succ_downloaded = set()

    def download(self):
        """
        @note: 下载数据
        """
        #若dst_dict中配置了des_file，则以之设置self.des_data_dict
        if not self.dst_dict.get("src_type", "").startswith("center") and "des_file" in self.dst_dict:
            self.load_yaml_des(self.dst_dict["des_file"])
        #若self.des_data_dict非空，遍历之，进行多轮下载
        fail = False
        if self.des_data_dict != None:
            for k in self.des_data_dict:
                if not self.des_data_dict[k].has_key("dst"):
                    _tmp = {"dst":k,"yaml_type":1}
                    dst_dict = dict(self.des_data_dict[k],**_tmp)
                else:
                    dst_dict = self.des_data_dict[k]
                for key in self.dst_dict:
                    if key not in dst_dict:
                        dst_dict[key] = self.dst_dict[key]
                self.downloadobj.set_path_element_dict(self.src_dict, dst_dict)
                if self.downloadobj.smart_download() == 0:
                    self.__succ_downloaded.add(k)
                else:
                    fail = True
            if self.command() != 0:
                fail = True
        else:
            #若self.des_data_dict为空，直接下载
            self.downloadobj.set_path_element_dict(self.src_dict, self.dst_dict)
            if self.downloadobj.smart_download() != 0:
                fail = True
            if self.command() != 0:
                fail = True
        if fail:
            return -1
        return 0

    def load_yaml_des(self,yaml_file):
        """
        @note: 加载yaml文件并设置为self.des_data_dict
        @param yaml_file: yaml文件路径
        @return: int
        """
        import yaml
        #使用try避免文件不存在等异常
        try:
            self.des_data_dict = yaml.load(open(yaml_file))
        except:
            return -1
        return 0

    def downloaded(self):
        """
        @note: 返回成功下载的element集合
        @return: 成功下载的element集合
        """
        return self.__succ_downloaded

    def command(self):
        """
        @note:执行element_file中的配置项  cmd的shell命令内容，该内容被完全执行
        """
        if self.dst_dict.has_key("cmd") and self.dst_dict["cmd"] <> None:
            return self.downloadobj.sys.xd_system("cd %s && %s"%(self.downloadobj.host_info["path"],self.dst_dict["cmd"]),pflag=True)
        return 0

