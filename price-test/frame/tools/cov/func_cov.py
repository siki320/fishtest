#!/usr/bin/env python
#-*- encoding:utf-8 -*-
import string
import os
import hashlib

class Cov_Global:
    func_cov_mode=False

class Func_Cov:
    desc = "函数覆盖率类，用于分析、生成覆盖率文件 和 建立正排、倒排"

    def __init__(self):
        """ 初始化函数 """
        pass
     
    def analyse_cov(self, src_covfile_path, des_funcov_path, src_path="../"):
        """ 分析 src_covfile_path 路径下所有覆盖率文件，生成函数覆盖文件，放在des_funcov_path """
        if not os.path.exists(src_covfile_path) or not os.path.exists(des_funcov_path):
            print src_covfile_path+" or "+des_funcov_path+" is not exist"
            return -1
            
        src_covfile_list = os.listdir(src_covfile_path)
        for src_covfile in src_covfile_list:
            str_tmp = "covfn -f "+src_covfile_path+"/"+src_covfile+" "+ src_path +" -c > " \
                    +des_funcov_path+"/"+src_covfile+" 2>/dev/null"
            os.system(str_tmp)
        return 0
    
    def gen_zhengpai(self, src_funcov_path, des_path):
        """ 根据函数覆盖率文件，生成倒排和正排"""
        if not os.path.exists(src_funcov_path) or not os.path.exists(des_path):
            print src_funcov_path+" or "+des_path+" is not exist"
            return -1
            
        src_funcovfile_list = os.listdir(src_funcov_path)
        zhengpai_write_fp=open(des_path+'/zhengpai.txt','w+')
        daopai_write_fp=open(des_path+'/daopai.txt','w+')
        zhengpai_dict = {}
        daopai_dict = {}
        
        for src_funcovfile in src_funcovfile_list:
            os.system("sed -i \'s/(.*)/()/g\' "+src_funcov_path+'/'+src_funcovfile) 
            file_read=open(src_funcov_path+'/'+src_funcovfile,'r')
            lines=file_read.readlines()
            for line in lines:
                fields = line.split(',')
                if len(fields) == 7 and '1' == fields[3] :
                    process_field0_tmp = string.replace(fields[0], "\"", "")
                    process_field0_tmp_list = process_field0_tmp.split("::")
                    process_field0_str = process_field0_tmp_list[len(process_field0_tmp_list)-2]\
                            + "::" + process_field0_tmp_list[len(process_field0_tmp_list)-1]
                    process_field0_str2 = string.replace(process_field0_str, " ", "")
                    process_field0 = process_field0_str2.split('(')[0]
                    if zhengpai_dict.has_key(src_funcovfile)==False:
                        zhengpai_dict[src_funcovfile]=[]
                    zhengpai_dict[src_funcovfile].append(process_field0)
                    if daopai_dict.has_key(process_field0)==False:
                        daopai_dict[process_field0] = []
                    daopai_dict[process_field0].append(src_funcovfile)
            file_read.close()
            
        for key in zhengpai_dict.keys():
            case_list = string.join(zhengpai_dict[key], '---')
            write_line = key+'\t'+case_list+'\n'
            zhengpai_write_fp.write(write_line)
                                                
        for key in daopai_dict.keys():
            fun_list = string.join(daopai_dict[key], '---')
            write_line = key+'\t'+fun_list+'\n'
            daopai_write_fp.write(write_line)
            
        del zhengpai_dict
        del daopai_dict
        zhengpai_write_fp.flush()
        daopai_write_fp.flush()
        zhengpai_write_fp.close()
        daopai_write_fp.close()
        return 0
        
    def check_zhengpai(self, file_name, case_names):
        """ 查正排，判断正排中是否有指定的case名"""
        ret_list = []
        if not os.path.exists(file_name):
            print file_name+" file is not exist"
            return ret_list
            
        if 0 == len(case_names):
            print "function name is not null"
            return ret_list
        file_read_fp=open(file_name, 'r')
        zhengpai_dict = {}
        lines = file_read_fp.readlines()
        for line in lines:
            line2 = string.replace(line, "\n", "")
            fields = line2.split('\t')
            case_name = string.replace(fields[0], '--', '/')
            if zhengpai_dict.has_key(case_name)==False:
                zhengpai_dict[case_name] = []
            list_tmp = fields[1].split('---')
            zhengpai_dict[case_name] = list_tmp
        file_read_fp.close()
                                               
        for one_case_name in case_names.split('---'):
            if zhengpai_dict.has_key(one_case_name):
                ret_list.extend(zhengpai_dict[one_case_name])

        del zhengpai_dict
        return ret_list

    def get_new_case_name(self, case_file_name, effect_case_list):
        """ 获得新加的case的list """
        ret_list = []
        if not os.path.exists(case_file_name):
            print case_file_name+" file is not exist"
            return ret_list

        old_case_list = []
        file_read_fp=open(case_file_name, 'r')
        lines = file_read_fp.readlines()
        for line in lines:
            line2 = string.replace(line, "\n", "")
            old_case_list.append(line2)

        for case_name in effect_case_list:
            if 0 == old_case_list.count(case_name):
                ret_list.append(case_name)

        return ret_list
            
    def get_one_case_from_casename(self, case_file_name, effect_case_list):
        """ 从case_name.txt中选出一个case"""
        ret_list_tmp = []
        if os.path.exists(case_file_name):
            case_file_fp=open(case_file_name, 'r')
            case_name_lines = case_file_fp.readlines()
            case_name_lines.sort()
            for one_case_name_line in case_name_lines:
                right_one_case_name=string.replace(one_case_name_line, '--', '/')
                if 0 != effect_case_list.count(right_one_case_name):
                    ret_list_tmp.append(right_one_case_name)
                    print "get one case: "+right_one_case_name
                    break
            case_file_fp.close()
        return ret_list_tmp
 

    def check_daopai(self, daopai_file_name, case_file_name, fun_names, effect_case_list):
        """ 查倒排，判断倒排中是否有指定的函数名 """
        ret_list = []
        temp_list = []
        
        if not os.path.exists(daopai_file_name):
            print daopai_file_name+" file is not exist"
            return ret_list
            
        if 0 == len(fun_names):
            print "function name is null"
            temp_list = self.get_one_case_from_casename(case_file_name, effect_case_list)
            ret_list.extend(temp_list)
            return ret_list
            
        file_read_fp=open(daopai_file_name, 'r')
        daopai_dict = {}
        daopai_dict_only_funname = {}
        lines = file_read_fp.readlines()
        for line in lines:
            line2 = string.replace(line, "\n", "")
            fields = line2.split('\t')
            if daopai_dict.has_key(fields[0])==False:
                daopai_dict[fields[0]] = []
            fields0s=fields[0].split('::')
            funname=fields0s[len(fields0s)-1]
            if daopai_dict_only_funname.has_key(funname)==False:
                daopai_dict_only_funname[funname] = []
            list_tmp = fields[1].split('---')
            daopai_dict[fields[0]] = list_tmp
            daopai_dict_only_funname[funname].extend(list_tmp)
        file_read_fp.close()

        for one_fun_name in fun_names.split('---'):
            if daopai_dict.has_key(one_fun_name):
                for case_name in daopai_dict[one_fun_name]:
                    if 0 == ret_list.count(string.replace(case_name, '--', '/')):
                        ret_list.append(string.replace(case_name, '--', '/'))
            else:
                if daopai_dict_only_funname.has_key(one_fun_name):
                    for case_name in daopai_dict_only_funname[one_fun_name]:
                        if 0 == ret_list.count(string.replace(case_name, '--', '/')):
                            ret_list.append(string.replace(case_name, '--', '/'))
        if len(effect_case_list) == 0:
            del daopai_dict
            del daopai_dict_only_funname
            return ret_list
        
        templist = []
        templist.extend(ret_list) 
        for ret_case in templist:
            if 0 == effect_case_list.count(ret_case):
                ret_list.remove(ret_case)

        if len(ret_list) == 0:
            temp_list = self.get_one_case_from_casename(case_file_name, effect_case_list)
            ret_list.extend(temp_list)
               
        del daopai_dict
        del daopai_dict_only_funname
        return ret_list
    
    def gen_all_casename(self, read_file_name, write_file_name):
        """ 查正排，返回所有case的名字 """
        if not os.path.exists(read_file_name):
            print read_file_name+" file is not exist"
            return -1
            
        if 0 == len(read_file_name) or 0 == len(write_file_name):
            print "file name is null"
            return -1
        
        case_name_list = []
        file_read_fp=open(read_file_name, 'r')
        file_write_fp=open(write_file_name, 'w+')
        lines = file_read_fp.readlines()
        for line in lines:
            line2 = string.replace(line, "\n", "")
            fields = line2.split('\t')
            case_name = string.replace(fields[0], '--', '/')
            case_name_list.append(case_name)
        file_read_fp.close()
        
        case_name_str = '\n'.join(case_name_list)
        file_write_fp.write(case_name_str)
                                               
        del case_name_list
        file_write_fp.close()
        return 0

    def gen_repeat_case(self, cov_file_path, result_path):
        """ 生成重复的case """
        if not os.path.exists(cov_file_path) or not os.path.exists(result_path):
            print cov_file_path+" or "+result_path+" is not exist"
            return -1
            
        cov_file_list = os.listdir(cov_file_path)
        repeat_case_fp=open(result_path+'/repeat_case.txt','w+')
        cov_file_md5_dict = {}
        for file in cov_file_list:
            m=hashlib.md5()
            file_fp=open(cov_file_path+"/"+file, 'r')
            m.update(file_fp.read())
            file_fp.close()
            file_md5=m.hexdigest()
            rew_case_name=string.replace(file, '--', '/')
            if cov_file_md5_dict.has_key(file_md5)==False:
                cov_file_md5_dict[file_md5]=[]
            cov_file_md5_dict[file_md5].append(rew_case_name)

        repeat_case_fp.write("覆盖率相同的case有：\n")
        #遍历dict，生成md5相同的case
        repeat_case_str=""
        for key in cov_file_md5_dict.keys():
            if len(cov_file_md5_dict[key]) > 1:
                repeat_case_str=""
                for case_name in cov_file_md5_dict[key]:
                    repeat_case_str=repeat_case_str+case_name+"  "
                repeat_case_str=repeat_case_str+"\n"
                repeat_case_fp.write(repeat_case_str)

        repeat_case_fp.close()
