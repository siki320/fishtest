# -*- coding: GB18030 -*-
"""
@author: guoan
@date: Nov 29, 2011
@summary: element������
@version: 1.1.0.0
@copyright: Copyright (c) 2011 XX, Inc. All Rights Reserved
"""
class Element(object):
    def __init__(self,**args):
        """
        @note:downloadobj \ src_dict \ dst_dict������baseobj�г�ʼ����
        ���Ƕ�element�������κ����飬��Ϊ������ʵ����element����Ϣ
        @param args: ����������Ŀǰֻ��name,file_path,downloader,src,dst,des���ܱ�ʹ��
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
        @note: ��������
        """
        #��dst_dict��������des_file������֮����self.des_data_dict
        if not self.dst_dict.get("src_type", "").startswith("center") and "des_file" in self.dst_dict:
            self.load_yaml_des(self.dst_dict["des_file"])
        #��self.des_data_dict�ǿգ�����֮�����ж�������
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
            #��self.des_data_dictΪ�գ�ֱ������
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
        @note: ����yaml�ļ�������Ϊself.des_data_dict
        @param yaml_file: yaml�ļ�·��
        @return: int
        """
        import yaml
        #ʹ��try�����ļ������ڵ��쳣
        try:
            self.des_data_dict = yaml.load(open(yaml_file))
        except:
            return -1
        return 0

    def downloaded(self):
        """
        @note: ���سɹ����ص�element����
        @return: �ɹ����ص�element����
        """
        return self.__succ_downloaded

    def command(self):
        """
        @note:ִ��element_file�е�������  cmd��shell�������ݣ������ݱ���ȫִ��
        """
        if self.dst_dict.has_key("cmd") and self.dst_dict["cmd"] <> None:
            return self.downloadobj.sys.xd_system("cd %s && %s"%(self.downloadobj.host_info["path"],self.dst_dict["cmd"]),pflag=True)
        return 0

