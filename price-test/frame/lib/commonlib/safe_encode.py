# -*- coding: GB18030 -*-
'''
Created on Mar 30, 2012

@author: caiyifeng<caiyifeng>
'''

import re
from frame.lib.thirdlib import chardet      # trigger chardet/__init__.py codes


def mydetect(aBuf):
    '''@summary: ��дchardet��detect��ʹ���ַ�����ѡ�������ecom��Ʒ��'''
    from charsetgroupprober import CharSetGroupProber
    from utf8prober import UTF8Prober
    from gb2312prober import GB2312Prober
    
    class MyMBCSGroupProber(CharSetGroupProber):
        def __init__(self):
            '''@summary: ֻ����gb��utf-8'''
            CharSetGroupProber.__init__(self)
            self._mProbers = [ \
                UTF8Prober(),
                GB2312Prober()]
            self.reset()
    
    
    import universaldetector
    
    u = universaldetector.UniversalDetector()
    u._mCharSetProbers = [MyMBCSGroupProber()]  # ֻ���gb��utf-8
    u.reset()
    u.feed(aBuf)
    u.close()
    return u.result
    

def safe_encode(s, enc):
    '''@summary: ��sת��Ϊ���ϱ�������enc���ַ���'''
    # �²�s�ı�������
    e = mydetect(s)["encoding"]
    try:
        return s.decode(e).encode(enc)
    except Exception:
        # ת�벻�ɹ�
        return safe_ascii(s)
    
def safegb(s):
    '''@summary: ��sת��Ϊgb18030�Ϸ����ַ���'''
    return safe_encode(s, enc="gb18030")

def safe_ascii(s):
    '''@summary: ��string�еķ�ascii�ַ���ת��Ϊ?'''
    return re.sub("[^\x00-\x7f]", "?", s)
    

def _test_safegb():
    ascii_str = "abcefg"
    gb_str = "abc����efg"
    utf_str = "abc����efg".decode("gb18030").encode("utf-8")
    mix_str = gb_str + utf_str
    
    print "ascii_str", safegb(ascii_str)
    print "gb_str", safegb(gb_str)
    print "utf_str", safegb(utf_str)
    print "mix_str", safegb(mix_str)

if __name__ == "__main__":
    _test_safegb()

