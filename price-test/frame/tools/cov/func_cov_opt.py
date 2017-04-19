#!/usr/bin/env python
#-*- encoding:utf-8 -*-
import os
import sys

from frame.tools.cov.selected_pyname import Selected_Pyname
from frame.tools.cov.GetDiffCasePlus import GetDiffCasePlus
from frame.tools.cov.func_cov import *
from frame.lib.hbdblib.hdc import HDC
from frame.tools.cov.cppdifffuncparser import getDiffFuncList
HDC_MACHINE=""
class Func_Cov_Opt():

    def __init__(self, cov_mod_name):
        """ ³õÊ¼»¯º¯Êý """
        self.cov_bake_path = os.environ["COV_BAKE_PATH"]
        self.cov_mod_name = cov_mod_name
        pass

    def _init_bake_env(self):
        os.system("rm -rf "+self.cov_bake_path+"/output/cov*;mkdir -p "+self.cov_bake_path+"/output/cov1 "+self.cov_bake_path+"/output/cov2 "+self.cov_bake_path+"/output/cov3")

    def _init_conf(self):
        Cov_Global.func_cov_mode = True

    def init_env(self):
        self._init_conf()
        self._init_bake_env()
        
    def _uploadto_old_path(self, src_path):
        product_line=os.environ["PRODUCT_LINE"]
        hdc_passwd = os.environ["HDC_PASSWD"]
        hdc_path=HDC_MACHINE+":/home/hdc/dts/"+product_line+"/"+self.cov_mod_name+"/"
        hdc = HDC(product_line)
        hdc.install_client()
        hdc.set_write_passwd(hdc_passwd)
        hdc.single_download(hdc_path+"index","./index")
        if os.path.exists("./index"):
            index_fp = open("./index", "r")
            index_lines = index_fp.readlines()
            index_fp.close()
            new_index = "0"
            if "0" == index_lines[0][:-1]:
                new_index = "1"
            print "new_index:"+new_index
            os.system("echo "+new_index+" > ./index")
            hdc.single_upload("./index", hdc_path)
            hdc.inc_upload(src_path+"/*", hdc_path+"/"+new_index)
        
    def process_cov_data(self) :
        cov1_path=self.cov_bake_path+"/output/cov1/"
        cov2_path=self.cov_bake_path+"/output/cov2/"
        cov3_path=self.cov_bake_path+"/output/cov3/"
        cov_file=os.environ["COVFILE"]
        cov_file_list=os.listdir(cov1_path)
        if len(cov_file_list) > 1:
            func_cov_obj = Func_Cov()
            print "begin to analyse_cov..."
            ret1 = func_cov_obj.analyse_cov(cov1_path, cov2_path, "../../")
            if 0 == ret1:
                print "begin to gen_zhengpai..."
                ret2 = func_cov_obj.gen_zhengpai(cov2_path, cov3_path)
            if 0 == ret2:
                print "begin to gen_all_casename..."
                func_cov_obj.gen_all_casename(cov3_path + "zhengpai.txt", cov3_path+ "case_name.txt")
                #func_cov_obj.gen_repeat_case(cov2_path, cov3_path)
            #update cov data
            print "begin to upload file..."
            self._uploadto_old_path(cov3_path)
            print "begin to merge cov file..."
            shutil.copy(cov1_path+cov_file_list[0], cov_file)
            for file_name in cov_file_list:
                dtssystem("covmerge -c " + cov_file + " -f "+ cov_file +" "+ cov1_path + file_name)
            print "process cov data over"
 
class Select_Case():
    def __init__(self, local_case_list, cov_mod_name):
        """ ³õÊ¼»¯º¯Êý """
        self.local_case_list = local_case_list
        self.cov_mod_name = cov_mod_name
        pass

    def _download_new_path(self, des_path):
        product_line=os.environ["PRODUCT_LINE"]
        hdc_path=HDC_MACHINE+":/home/hdc/dts/"+product_line+"/"+self.cov_mod_name+"/"
        hdc = HDC(product_line)
        hdc.install_client()
        hdc.single_download(hdc_path+"index","./index")
        if os.path.exists("./index"):
            index_fp = open("./index", "r")
            index_lines = index_fp.readlines()
            index_fp.close()
            new_index = "0"
            if "1" == index_lines[0][:-1]:
                new_index = "1"
            print "new_index:"+new_index
            hdc.single_download(hdc_path+"/"+new_index+"/*",des_path)
 
    def get_select_case(self):
        """ Ñ¡Ôñcase """
        # process args join TestAbc:testabc TestAbc:testxyz as TestAbc:testabc,testxyz
        pys = []
        cases = []
        cov_src_path=os.environ["COV_SRC_PATH"]
        case_path_env=os.environ["CASE_PATH_ENV"]
        os.system("mkdir -p " + cov_src_path + "/output")
        self._download_new_path(cov_src_path + "/output")
        
        function_list = getDiffFuncList(cov_src_path,cov_src_path+"/output/svn_diff.txt")
        function_str = "---".join(function_list)
        func_cov_obj = Func_Cov()
        temp_cases=func_cov_obj.check_daopai(cov_src_path+'/output/daopai.txt',cov_src_path+'/output/case_name.txt',function_str,self.local_case_list)
        new_cases = func_cov_obj.get_new_case_name(cov_src_path+'/output/case_name.txt', self.local_case_list)
        checkdiffcase_obj = GetDiffCasePlus(cov_src_path+"/output/svn_diff.txt","ctr",case_path_env)
        mod_cases = checkdiffcase_obj.getDiffCase()
        for acase in temp_cases+new_cases+mod_cases:
            temp_fields=acase.split(":")
            if len(temp_fields)==1:
                cases.append(acase)
                pys.append(temp_fields[0])
                continue
            try:
                case_idx = pys.index(temp_fields[0])
                if -1 == cases[case_idx].find(temp_fields[1]):
                    cases[case_idx] += ","+temp_fields[1]
            except:
                cases.append(acase)
                pys.append(temp_fields[0])
        cases.sort()
        return cases 
