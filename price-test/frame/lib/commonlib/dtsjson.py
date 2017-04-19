# -*- coding: GB18030 -*-
'''
Created on Mar 30, 2012

@author: caiyifeng<caiyifeng>

@summary: ��json����һЩ��װ������ʵ����
'''

import json


class DtestJsonDecoder(json.JSONDecoder):
    '''@summary: Ĭ�ϵ�JSONDecoder�����е��ַ�������תΪunicode�������������иĽ���ת��ԭ��������ַ���'''
    def decode(self, s):
        '''@param s: json�ַ���'''
        ret = super(DtestJsonDecoder, self).decode(s)   # ���ø�����������õ����
        return self.tobyte(ret)     # ������е�unicodeתΪԭ���ı���
    
    def tobyte(self, obj):
        '''@summary: ��obj�е�unicodeתΪԭ���ı���'''
        if isinstance(obj, dict):
            ret = {}
            for k,v in obj.items():
                ret[k.encode(self.encoding)] = self.tobyte(v)   # dict���󣬱���key�����ݹ�tobyte value
            return ret
        
        elif isinstance(obj, list):
            return [self.tobyte(l) for l in obj]        # list���󣬵ݹ�tobyteÿһ��Ԫ��

        elif isinstance(obj, unicode):
            return obj.encode(self.encoding)            # unicode���󣬱���
        
        else:
            return obj


def load(fp, enc="gb18030"):
    '''@param enc: �ļ��ı������ͣ�Ĭ��Ϊgb18030'''
    return json.load(fp, encoding=enc, cls=DtestJsonDecoder)

def loads(s, enc="gb18030"):
    '''@param enc: �ַ���s�ı������ͣ�Ĭ��Ϊgb18030'''
    return json.loads(s, encoding=enc, cls=DtestJsonDecoder)

