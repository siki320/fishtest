# -*- coding: GB18030 -*-
'''
Created on Mar 30, 2012

@author: caiyifeng<caiyifeng>
'''

import re
from frame.lib.thirdlib import chardet      # trigger chardet/__init__.py codes


def mydetect(aBuf):
    '''@summary: 改写chardet的detect，使得字符集的选择更符合ecom产品线'''
    from charsetgroupprober import CharSetGroupProber
    from utf8prober import UTF8Prober
    from gb2312prober import GB2312Prober
    
    class MyMBCSGroupProber(CharSetGroupProber):
        def __init__(self):
            '''@summary: 只保留gb和utf-8'''
            CharSetGroupProber.__init__(self)
            self._mProbers = [ \
                UTF8Prober(),
                GB2312Prober()]
            self.reset()
    
    
    import universaldetector
    
    u = universaldetector.UniversalDetector()
    u._mCharSetProbers = [MyMBCSGroupProber()]  # 只检测gb和utf-8
    u.reset()
    u.feed(aBuf)
    u.close()
    return u.result
    

def safe_encode(s, enc):
    '''@summary: 将s转化为符合编码类型enc的字符串'''
    # 猜测s的编码类型
    e = mydetect(s)["encoding"]
    try:
        return s.decode(e).encode(enc)
    except Exception:
        # 转码不成功
        return safe_ascii(s)
    
def safegb(s):
    '''@summary: 将s转化为gb18030合法的字符串'''
    return safe_encode(s, enc="gb18030")

def safe_ascii(s):
    '''@summary: 将string中的非ascii字符，转化为?'''
    return re.sub("[^\x00-\x7f]", "?", s)
    

def _test_safegb():
    ascii_str = "abcefg"
    gb_str = "abc中文efg"
    utf_str = "abc中文efg".decode("gb18030").encode("utf-8")
    mix_str = gb_str + utf_str
    
    print "ascii_str", safegb(ascii_str)
    print "gb_str", safegb(gb_str)
    print "utf_str", safegb(utf_str)
    print "mix_str", safegb(mix_str)

if __name__ == "__main__":
    _test_safegb()

