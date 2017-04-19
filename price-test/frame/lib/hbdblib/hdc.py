# -*- coding: GB18030 -*-
"""
@author: maqi
"""

import os
from frame.lib.hbdblib.base import HBDBBase
from frame.lib.commonlib.dtssystem import dtssystem

class HDC(HBDBBase):
    def __init__(self, user, *args, **kwargs):
        super(HDC, self).__init__(user, *args, **kwargs)
        self.client_path = os.path.expanduser("~/.HDC_CLIENT")
        self.hdc_bin_path = self.client_path + "/hdc"

    def set_write_passwd(self,passwd):
        self.passwd = passwd

    def install_client(self):
        clean_str = "rm -rf hdc"
        dtssystem(clean_str)
        wget_str = ""
        dtssystem(wget_str)
        dtssystem("chmod 755 hdc;mkdir -p %s;mv hdc %s" % (self.client_path,self.client_path))

    def raw_ls(self,src):
        return "%s -ls %s" % (self.hdc_bin_path,src)

    def raw_mkdir(self,src):
        return "%s -mkdir -p %s %s" % (self.hdc_bin_path,self.passwd,src)

    def raw_rm(self,src):
        return "%s -rmr -p %s %s" % (self.hdc_bin_path,self.passwd,src)

    def raw_put(self,src,des):
        return "%s -put -p %s %s %s" % (self.hdc_bin_path,self.passwd,src,des)

    def raw_inc_put(self,src,des):
        return "%s -inc-put -p %s %s %s" % (self.hdc_bin_path,self.passwd,src,des)

    def raw_get(self,src,des):
        return "%s -get %s %s" % (self.hdc_bin_path,src,des)

    def raw_inc_get(self,src,des):
        return "%s -inc-get %s %s" % (self.hdc_bin_path,src,des)

if __name__ == '__main__':
    h = HDC("im")
    h.install_client()


