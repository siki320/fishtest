# -*- coding: GB18030 -*-
'''
Created on Dec 6, 2011

@author: caiyifeng<caiyifeng>
INSPIRED BY KV_Conf of tanyi
@summary: ����key-value���͵�conf�ļ�
@modified : geshijing Sep 27,2012
summary : ���Ӷ��ڿ����ظ�key�������ļ���֧�֣����ݾɰ汾���й���
'''


class Kvconf(object):
    def __init__(self, filepath, sep=":",repeat=False):
        self.filepath = filepath
        self.sep = sep
        self.repeat = repeat
        self.kvdict = {}    # conf���key-value�ֵ�
        self.lines = []     # �����conf��򱣴�key��������ǣ�ע���У����У����򱣴�����

        self._load(repeat)    # ����conf�ļ�

    def setvalue(self, key, value,pos=0):
        if key not in self.kvdict:
            raise KeyError, "Unknown key[%s] in %s" % (key, self.filepath)
        elif pos >= len(self.kvdict[key]):
            raise KeyError, "Unexpect pos[%d] for key[%s] in %s" % (pos,key, self.filepath)
        self.kvdict[key][pos] = value

    def getvalue(self, key,pos=0):
        if key not in self.kvdict:
            raise KeyError, "Unknown key[%s] in %s" % (key, self.filepath)
        elif pos >= len(self.kvdict[key]):
            raise KeyError, "Unexpect pos[%d] for key[%s] in %s" % (pos,key, self.filepath)
        return self.kvdict[key][pos]

    def addvalue(self, key, value,repeat=False):
        if not repeat:
            if key in self.kvdict:
                raise Exception, "Already has key[%s] in %s" % (key, self.filepath)
            self.kvdict[key] = [value]
            self.lines.append(key)
        else:
            if key not in self.kvdict:
                self.kvdict[key] = []
            self.kvdict[key].append(value)
            self.lines.append(key)

    def delvalue(self, key, realdel=False,pos=0):
        '''
        @summary: ɾ��һ��������
        @param realdel:
         - True��ʾʵ��ɾ��
         - False��ʾע�͵���Ĭ�ϣ�
        '''
        if key not in self.kvdict:
            raise KeyError, "Unknown key[%s] in %s" % (key, self.filepath)
        elif pos >= len(self.kvdict[key]):
            raise KeyError, "Unexpect pos[%d] for key[%s] in %s" % (pos,key, self.filepath)
        idx = self.lines.index(key,pos+1)
        if not realdel:
            # ��ʵ��ɾ�������ע����
            self.lines.insert(idx+1, "#"+key+self.sep+self.kvdict[key][pos])

        # ɾ��ԭ����������
        del self.lines[idx]
        del self.kvdict[key][pos]

    def haskey(self, key,pos=0):
        if key in self.kvdict:
            return pos < len(self.kvdict[key])
        else:
            return False

    def __str__(self):
        '''@summary: ����conf�ļ��ı�'''
        ret = []

        for l in self.lines:
            if l in self.kvdict:
                ret.append(l + self.sep + self.kvdict[l][0])
                #��ԭ����key�ӵ����ȥ
                self.kvdict[l].append(self.kvdict[l][0])
                del self.kvdict[l][0]
            else:
                ret.append(l)

        return "".join([l+"\n" for l in ret])

    def dump(self):
        f = open(self.filepath, "w")
        f.write(str(self))
        f.close()

    def _load(self,repeat=False):
        f = open(self.filepath)

        for line in f:
            # �ж�ע����
            line = line.strip()
            if line.startswith("#"):
                self.lines.append(line.strip())
                continue

            # ���ݷָ����з֣�����зֳ�2��
            linesplit = line.split(self.sep, 1)
            if len(linesplit) == 2:
                # �зֳ���key-value
                k, v = linesplit
                k = k.strip()
                v = v.strip()

                if k in self.kvdict and not repeat:
                    # ��ͬ��key������
                    raise Exception, "Duplicated key[%s] in %s" % (k, self.filepath)
                if k not in self.kvdict:
                    self.kvdict[k] = []
                self.kvdict[k].append(v)
                self.lines.append(k)
            else:
                # ֻ�зֳ�1�Σ���������
                self.lines.append(line.strip())

        f.close()


def _test():
    filepath = raw_input("Enter conf filepath: ")
    kv = Kvconf(filepath)

    print "========= Original File content =========="
    print
    print kv

    print "======== Add key ========"
    kv.addvalue("caiyifeng", "xiaoguai")
    print
    print kv

    key = raw_input("Enter a key: ")

    print "========= Get original key ========"
    print key, ":", kv.getvalue(key)

    print "======== Set key ========"
    kv.setvalue(key, "xiaodai")
    print
    print kv

    print "========= Get key ========"
    print key, ":", kv.getvalue(key)

    print "========= Comment key =========="
    kv.delvalue(key)
    print
    print kv

    print "======== Delete key =========="
    kv.delvalue("caiyifeng", realdel=True)
    print
    print kv

if __name__ == "__main__":
    _test()

