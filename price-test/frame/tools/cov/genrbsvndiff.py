#!/usr/bin/env python
#-*- encoding:utf-8 -*-
import string
import os
import sys

class Genrb_Svndiff:
    desc = " 生成本rb和上一个rb之间的代码diff"

    def __init__(self):
        """ 初始化函数 """
        pass
     
    def _get_codediff(self, old_svn_path, new_svn_path):
        """ 获得本rb和上个rb的代码diff """
        """svn_path格式： https://svn."""
        cmd = "mkdir -p ../run_env; svn diff " + old_svn_path + " " + new_svn_path +"> ../run_env/svn_diff.txt"
        os.system(cmd)
        return 0

    def _get_casediff(self, old_svn_path, new_svn_path):
        """ 获得本rb和上个rb的 cts case diff """
        """svn_path格式： """
        cmd = "mkdir -p ../run_env; svn diff " + old_svn_path + "/cts/case " + new_svn_path +"/cts/case > ../run_env/cts_svn_diff.txt"
        os.system(cmd)
        return 0

    def _get_old_svn(self, new_svn):
        """ 根据新的svn，获得上一个版本svn """
        old_svn=""
        if 0 == len(new_svn):
            print "传入的new_svn为空"
            return old_svn
        
        fields = new_svn.split("/")
        length = len(fields)
        if 2 > length:
            print new_svn+"格式不正确"
            return old_svn
        
        fields2 = fields[length-1].split("_")
        if 3 > len(fields2):
            print new_svn+"格式不正确"
            return old_svn
        
        mod_name = fields2[0]
        versions = fields2[1]
        field3 = versions.split("-")
        if 2 > len(field3):
            print new_svn+"格式不正确"
            return old_svn
        
        version1 = versions.split("-")[0]
        version2 = versions.split("-")[1]
        version3 = versions.split("-")[2]
        version31 = str(int(version3)-1)

        if 0 > version31:
            print new_svn+"格式不正确"
            return old_svn
        
        old_ver = mod_name+ "_" + version1+ "-" + version2+ "-" +version31 +"_BRANCH"
        old_svn = string.replace(new_svn, fields[length-1], old_ver)
        return old_svn

    def _get_old_ctscase(self, old_svn):
        """ 根据 old_svn，check out出case文件夹 """
        if 0 == len(old_svn):
            print "old_svn为空，check out case文件夹失败"
            return -1
        
        cmd="rm -rf case_old; mkdir case_old ; svn co "+old_svn+"/cts/case case_old >/dev/null 2>&1"
        os.system(cmd)
        return 0

    def genrb_svndiff(self):
        """ 获得本rb和上一个rb的代码diff和cts case diff """
        cur_svn=""
        ret = os.popen("svn info| grep BRANCH").read()
        urls = ret.split("\n")
        for url in urls:
            if 0 != len(url) and "BRANCH" in url:
                temp_url=url.split(" ")[1]
                cur_svn=string.replace(temp_url, "/cts", "")
                print "当前rb svn: "+cur_svn
        
        if 0 == len(cur_svn):
            print "获得当前svn失败"
            return -1
        
        old_svn = self._get_old_svn(cur_svn)
        print "上一个rb svn: "+old_svn
        if 0 == len(old_svn):
            print "获得上一个rb的svn地址失败"
            return -1

        ret = self._get_codediff(old_svn, cur_svn)
        if 0 != ret:
            print "生成代码diff失败"
            return -1
        
        return 0

if __name__ == "__main__":
    genrb_svndiff_obj = Genrb_Svndiff()
    genrb_svndiff_obj.genrb_svndiff()
