# -*- coding: GB18030 -*-
'''
Created on Mar 30, 2012

@author: caiyifeng<caiyifeng>

@summary: 对json包的一些包装，增加实用性
'''

import json


class DtestJsonDecoder(json.JSONDecoder):
    '''@summary: 默认的JSONDecoder将所有的字符串对象转为unicode。本解码器进行改进：转回原来编码的字符串'''
    def decode(self, s):
        '''@param s: json字符串'''
        ret = super(DtestJsonDecoder, self).decode(s)   # 调用父类解码器，得到结果
        return self.tobyte(ret)     # 将结果中的unicode转为原来的编码
    
    def tobyte(self, obj):
        '''@summary: 将obj中的unicode转为原来的编码'''
        if isinstance(obj, dict):
            ret = {}
            for k,v in obj.items():
                ret[k.encode(self.encoding)] = self.tobyte(v)   # dict对象，编码key，并递归tobyte value
            return ret
        
        elif isinstance(obj, list):
            return [self.tobyte(l) for l in obj]        # list对象，递归tobyte每一个元素

        elif isinstance(obj, unicode):
            return obj.encode(self.encoding)            # unicode对象，编码
        
        else:
            return obj


def load(fp, enc="gb18030"):
    '''@param enc: 文件的编码类型，默认为gb18030'''
    return json.load(fp, encoding=enc, cls=DtestJsonDecoder)

def loads(s, enc="gb18030"):
    '''@param enc: 字符串s的编码类型，默认为gb18030'''
    return json.loads(s, encoding=enc, cls=DtestJsonDecoder)

