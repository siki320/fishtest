# -*- coding:gbk -*-
import re
import os
import sys
from frame.tools.cov.selected_pyname import Selected_Pyname

class SplitCase(object):
    def __init__(self):
        self.time_dict = {}
        self.left_case = []
        self.total_time = 0
        self.split_num = 0
        self.case_dict = {}

    def read_result(self, resultfile):
        """
        @summary 读取result文件,获取case的运行时间
        """
        file_exist = os.path.exists(resultfile)
        if file_exist == False:
            return 0
        rf = file(resultfile)
        for line in rf:
            line = line.rstrip()
            ma = re.match("(.*?\.py)\tP\t\t\t(\d+)",line)
            if ma:
                cost = int(ma.group(2))
                self.time_dict[ma.group(1)] = cost
                self.total_time += cost
        rf.close()

    def read_casedirs(self, casedirs=[]):
        selected_pylist = []
        selected_pyname_obj = Selected_Pyname()
        selected_pylist = selected_pyname_obj.get_selected_pyname()
        if len(selected_pylist) > 0:
            print "selected_pylist is not null"
            for pyname in selected_pylist:
                print pyname
                if self.time_dict.has_key(pyname):
                    self.case_dict[pyname] = 0
                else:
                    self.left_case.append(pyname)
            return 1
        for casedir in casedirs:
            files = os.listdir(casedir)  
            casedir = casedir.rstrip('/')
            for f in files:  
                #print casedir + '/' + f
                if(os.path.isdir(casedir + '/' + f)):  
                    if(f[0] == '.'):  
                        continue
                    else:  
                        self.read_casedirs([casedir + '/' + f])
                if(os.path.isfile(casedir + '/' + f)):  
                    name, ext = os.path.splitext(f)
                    if ext == ".py":
                        if self.time_dict.has_key(casedir + '/' + f):
                            self.case_dict[casedir+'/'+f] = 0
                            pass
                        else:
                            self.left_case.append(casedir + '/' + f)
                    else:
                        pass
        return 0

    def gen_command(self, output):
        total_case = 0
        of = file(output,"w")
        for grp in self.case_group:
            total_case += len(grp)
            case_str = " ".join(grp)
            case_str = "source ~/.bash_profile; dts_run --cluster -a "+case_str
            if len(case_str)>4095:
                raise Exception,"command is too long"
            of.write(case_str+"\n")
        of.flush()
        of.close() 
    def gen_command_ori(self, output):
        total_case = 0
        of = file(output,"w")
        for grp in self.case_group:
            total_case += len(grp)
            case_str = " ".join(grp)
            case_str = "sh autorun.sh --cluster -a "+case_str
            if len(case_str)>4095:
                raise Exception,"command is too long"
            of.write(case_str+"\n")
        of.flush()
        of.close() 

    def split_case_ex(self, resultfile, group_time, casedir=[]):
        self.read_result(resultfile)
        ret = self.read_casedirs(casedir)
        if 0 != ret:
            group_time = group_time/2
        self.case_group = []
        g_total_time = 0 #group case的时间
        g_idx = 0        #group 索引
        while 1:
            one_group_time = 0
            self.case_group.append([])
            all_case_finished = True
            for case in self.case_dict.keys():
                if self.case_dict[case] == 1:
                    continue
                all_case_finished = False
                acase_time = self.time_dict[case]/1000.0
                if len(self.case_group[g_idx])>0 and \
                    one_group_time+acase_time>group_time:
                    #队列有case,当前case不能加入队列
                    continue
                self.case_group[g_idx].append(case)
                self.case_dict[case] = 1
                one_group_time += acase_time
                g_total_time += acase_time
            if all_case_finished == True:
                if len(self.case_group[g_idx])==0: #最后一个队列为空时，将其删除
                    self.case_group.pop()
                break
            print "%d组实际时间:%fs "%(g_idx,one_group_time)
            g_idx += 1
    
        print "总共%d组,总时间:%f s"%(len(self.case_group),g_total_time)
        g_idx = 0
        
        #主要是用于处理dts2下模块第一次调用时候没有time.txt的情况
        if len(self.case_group) == 0:
            for case in self.left_case:
                self.case_group.append([])

        for case in self.left_case:
            if g_idx >= len(self.case_group):
                g_idx = 0
            self.case_group[g_idx].append(case)
            g_idx += 1
            

if __name__ == "__main__":
    sc = SplitCase()
    sc.split_case_ex(sys.argv[1], int(sys.argv[2]), sys.argv[4:5])
    para_num = len(sys.argv) - 1
    if para_num == 4:
        sc.gen_command(sys.argv[3])
    else:
        sc.gen_command_ori(sys.argv[3])

