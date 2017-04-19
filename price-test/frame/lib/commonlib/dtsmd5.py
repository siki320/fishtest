# -*- coding: GB18030 -*-
"""
@author: youguiyan01
@date: Mar 5, 2012
@summary: md5����
@version: 1.0.0.0
@copyright: Copyright (c) 2012 XX, Inc. All Rights Reserved
"""
import os
import hashlib
import sys
import re
class MD5:
    """
    @note: md5������,֧�ּ����ļ���Ŀ¼��md5ֵ��ͬʱ������� ignore�б�
    """

    def __init__(self):
        self._ignore_list = []
        self.result = []

    def __str__(self):
        """
        @note: �����string�У�ÿ��һ���ļ�����һ��ֵ��MD5���ڶ����ǵ�ַ
        """

        result_list = []
        for result in self.result:
            if len(result) ==2:
                result_list.append(result["md5"]+"  "+ result["path"])
        return "\n".join(result_list)
    
    def add_ignore(self,file_name):
        """
        @note: ��ӹ����б�֧��������ʽ���������ļ������ļ��У�ֻҪ·���к��иôʣ����ᱻ����
        @param file_name:��Ҫ���˵�����
        """
        self._ignore_list.append(file_name)
        
    def _md5_file(self,file_path,seg_num=128,read_power=0):
        """
        @note: �����ļ���md5ֵ,���ļ��ֶΣ���ÿһ���ж�ȡһ�����ȵ�ֵ����md5����
        @param file_path:�ļ�·��
               seg_num: �ļ��ֶεĸ��� 
               read_power:ÿ�ζ�ȡ���ȵ�ָ��
        @return result�ֵ䣬key��md5��path���� 
        """
        result = {}
        result["path"] = file_path
        #read_size��С��2*13
        read_size = 2**(13+read_power)
        fp = open(file_path,"rb")
        #�ļ���С���ڷֶ��м����ļ���С������
        file_size = os.path.getsize(file_path)
        md5_value = hashlib.md5()
        #�ֶεĸ�����������ĳ���̫�󣬿��ܵ���û�а취����ô��Σ�
        #���������ȥ��������Сֵ
        seg_num = file_size/read_size > seg_num and seg_num or file_size/read_size+1
        for i in range(seg_num):
            #��λ���öεĳ�ʼλ��
            skig_size = (i*file_size)/seg_num
            fp.seek(skig_size,0)
            #��read_size���ȵ�����
            tmp = fp.read(read_size)
            if not tmp:
                break
            #����md5ֵ
            md5_value.update(tmp)

        result["md5"]=md5_value.hexdigest()
        fp.close()
        return result

    def _is_ignore(self,path):
        """
        @note:  �ж��Ƿ��ڹ����б��У���Ҫ������
        @return True:��Ҫ������
                False:����Ҫ������
        @param  path:��Ҫ�жϵ�·��
        """
        for pattern in self._ignore_list:
            if re.search(pattern,path):
                return True
        return False
    def _md5_dir(self,file_path,seg_num=8096,read_power=0):
        """
        @note: ����Ŀ¼��md5�����еݹ���� 
        @param file_path:�ļ�·��
               seg_num: �ļ��ֶεĸ��� 
               read_power:ÿ�ζ�ȡ���ȵ�ָ��
        @return ����ֵ��һ���б��б���ÿһ��Ԫ�ض����ֵ�
                key��md5��path���� 
        """
        result = []
        dirs = os.listdir(file_path)
        for one_dir in dirs:
            path = file_path + os.sep + one_dir
            #�ж��Ƿ��ڹ����б���
            if self._is_ignore(path):
                continue
            if os.path.isdir(path):
                result += self._md5_dir(path,seg_num,read_power)
            else:
                result += [self._md5_file(path,seg_num,read_power)]
        return result

    def md5sum(self,file_path,seg_num=8096,read_power=0):
        """
        @note: ����md5 
        @param file_path:�ļ�·��
               seg_num: �ļ��ֶεĸ��� 
               read_power:ÿ�ζ�ȡ���ȵ�ָ��
        @return ����ֵ��һ���б��б���ÿһ��Ԫ�ض����ֵ�
                key��md5��path���� 
        """
        self.result = []
        #�ļ�
        if os.path.isfile(file_path):
            #�����ļ���Ҫ�����ж��Ƿ���Ҫ����
            if self._is_ignore(file_path):
                self.result =[]
            else:
                self.result = [self._md5_file(file_path,seg_num,read_power)]
        #Ŀ¼
        elif os.path.isdir(file_path):
            self.result = self._md5_dir(file_path,seg_num,read_power)
        else: 
            self.result = []
        return self.result

if __name__== "__main__":
    import sys
    a=MD5()
    a.add_ignore("svn")
    a.add_ignore("test")
    a.md5sum(sys.argv[1],128,10)
    print str(a)
