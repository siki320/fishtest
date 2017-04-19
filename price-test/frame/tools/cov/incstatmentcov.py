
#!/usr/bin/env python
# encoding: GB18030 
"""
incstatmentcov.py

Created by ypp on 2012-02-29.
"""
import commands
import os
import sys
import getopt
import linecache
import re
import shutil
from datetime import datetime

G = {}
G["CURRENT_DIR"] = os.getcwd()
G["TTY_FATAL"] = 1
G["TTY_PASS"] = 2
G["TTY_TRACE"] = 4
G["TTY_INFO"] = 8

EXECUTED_YES = 0
EXECUTED_NO = 1
EXECUTED_IGNORE = 2
TTY_CLEAR = 0
TTY_RED = 1
TTY_GREEN = 2
TTY_BLUE = 3
TTY_MODE_COLOR = {}
TTY_MODE_COLOR[TTY_CLEAR] = "0"
TTY_MODE_COLOR[TTY_RED] = "1;31"
TTY_MODE_COLOR[TTY_GREEN] = "1;32"
TTY_MODE_COLOR[TTY_BLUE] = "1;34"
FILE_MODE_COLOR = {}
FILE_MODE_COLOR[TTY_CLEAR] = ""
FILE_MODE_COLOR[TTY_RED] = "-->"
FILE_MODE_COLOR[TTY_GREEN] = "  X"
FILE_MODE_COLOR[TTY_BLUE] = "  O"

def pretty_print(tty_mode,text,newline=True):
    print"\x1b[%sm%s\x1b[m" % (TTY_MODE_COLOR[tty_mode], text),
    if newline:
        print

def file_print(tty_mode,text,newline=True):
    #print "{:<5}{}".format(FILE_MODE_COLOR[tty_mode], text),
    print"%-5s %s" %(FILE_MODE_COLOR[tty_mode], text),
    if newline:
        print

class CodeBlock:
    def __init__(self):
        self.startline = 0
        self.endline = 0
    def set_start_end(self,startline,endline):
        self.startline = startline
        self.endline = endline
    def get_start_end(self):
        return self.startline,self.endline
        
def index_of(str_,ch,idx):
    idx_found = 0
    len_ = len(str_)
    for i in range(0,len_,1):
        if  str_[i] == ch:
            idx_found += 1
            if idx_found == idx:
                return i
    return -1

def is_legal_file(path):
    ext_list = [".cc",".c",".cpp",".h",".hpp"]
    file_name = os.path.basename(path)
    name,ext = os.path.splitext(file_name)
    pattern = re.compile('test_')
    #pattern = re.compile('[\/]*test\/')
    ret = 0
    if (not pattern.search(path)) and ext in ext_list:
        ret = 1
    return ret

def code_diff(svn_diff,result={}):
    global G
    flag = "Index"
    flag_len = len(flag)
    file_name = ""
    changed_indeed = 0
    line_no1 = 0
    line_no2 = 0
    skip_the_file = 0
    startline = 0
    prelabel = " "
    fileIN = open(svn_diff, "r")
    for line in fileIN:
        line = line.strip('\n')
        if line[0:flag_len] == flag:
            file_name = line[flag_len+2:]
            if is_legal_file(file_name) == 1:
                skip_the_file=0
                result[file_name]=[]
            else:
                skip_the_file=1
            changed_indeed=0
            continue
        if line[0:3] == "---" or line[0:3] == "+++" :
            continue
       # if line.strip() and 0x4e00<ord(line.strip()[0])<0x9fa6:
       #     continue
        if skip_the_file == 1:
            continue
        if line[0:2] == "@@":
            prelabel = " "
            pattern = re.compile("^@@ \-[0-9]+,[0-9]+ \+0,0 @@$")
            if not pattern.search(line):
                changed_indeed=1
            comma_idx = index_of(line, ",", 1)
            line_no1 = int(line[4:comma_idx])
            plus_idx = index_of(line, "+", 1)
            comma_idx = index_of(line, ",", 2)
            line_no2 = int(line[plus_idx+1:comma_idx])
        elif changed_indeed == 1:
            if line[0:1] == "-":
                if prelabel == "+":
                    a = CodeBlock()
                    a.set_start_end(startline,line_no2-1)
                    result[file_name].append(a)
                prelabel = "-"
                line_no1 += 1
            elif line[0:1] == "+":
                if prelabel != "+":
                    startline = line_no2
                prelabel = "+"
                line_no2 += 1
            else:
                if prelabel == "+":
                    a = CodeBlock()
                    a.set_start_end(startline,line_no2-1)
                    result[file_name].append(a)
                prelabel = " "
                line_no1 += 1
                line_no2 += 1
    fileIN.close()
#    for key in result:
#        print len(result[key])
#        for block in result[key]:
#            a,b = block.get_start_end()
#            print a,b

def modfun(result={},modfun_result={}):
    for key in result:
        if len(result[key]) != 0:
            modfun_result[key] = result[key]

#    for key in modfun_result:
#        print len(modfun_result[key])
#        for block in modfun_result[key]:
#            a,b = block.get_start_end()
#            print a,b

class MetaFile:
    def __init__(self,input_path,output_path):
        self.file_path = input_path
        self.source_path = None
        self.r=re.compile('\n(?P<flag>[tfx\-\>]*)\s*(?P<lineno>[0-9]+)',re.I)

             
    def __find_ch(self,source_str, pos, ch):
        end = pos
        while end < len(source_str):
            if source_str[end] == ch:
                return end+1
            end += 1
        return -1

    def __get_statement(self, source_str, pos):
        end = pos
        left_pos = 0
        right_pos = 0
        is_for = False
        while end < len(source_str): 
            if source_str[end] == ";": #find a statment, bug it not in for
                return source_str[pos:end],end
            if source_str[end:end+3] == "for":
                end += 3
                is_for = True
                continue
            if is_for and source_str[end] == "(":
                left_pos = end
                end = self.__find_ch(source_str,end,")")
                right_pos = end
                if end == -1:
                    raise Exception,"find ) error"
                is_for = False
                continue
            end += 1
        end = -1
        return source_str[pos:end],end

    def __get_line(self,source_str):
        end = source_str.find("\n")
        return source_str[0:end],end

    def __get_lineno(self,source_str,pos):
        temp = pos-1
        while temp > 0:
            if source_str[temp] == "\n":
                break
            temp -= 1
        #print "__get_lineno", source_str[temp:pos],temp,pos
        ma = self.r.search(source_str[temp:pos])
        if ma:
            return int(ma.group('lineno'))
        else:
            return -1
        
        return source_str[pos:end],end
    def __jump_block(self,source_str,pos):
        end = pos
        while end < len(source_str):
            if source_str[end] == "{":
                end = self.__jump_block(source_str,end+1)
                continue
            if source_str[end] == "}":
                #print "__jump_block:",end
                return end+1
            end += 1
        raise Exception, " can not find },pos=%d:%d"%(pos,end)

    def parseBlock(self,source_str, block):
        block_start=False
        pos = 0
        if block.flag_str.find("X")>=0:
            block.excuted = True
        if block.flag_str.find("T")>=0:
            block.excuted = True
        if block.flag_str.find("t")>=0:
            block.excuted = True
        (statement,stm_pos)=self.__get_statement(source_str,0)
        while pos < len(source_str): 
            if block_start==False and stm_pos < pos: #no {, it has a just one statment
                block.end_line = self.__get_lineno(source_str,pos)
                if block.end_line==-1:
                    block.end_line = block.start_line
                break
            if source_str[pos] == "{": #block start
                block_start = True 
                b_pos = pos
                try:
                    pos=self.__jump_block(source_str,pos+1)
                except:
                    raise Exception,"parse block fail%s"%source_str[pos:-1]
                e_pos = pos
                #print "============",source_str[b_pos:e_pos],"==========="
                block.end_line = self.__get_lineno(source_str,pos)
                if block.end_line==-1:
                    block.end_line = block.start_line
                break
            pos += 1
        return pos    

    def parseSourceCovbr(self,srcblocks=[]):
        """
        @param [in]source_covbr_file:sourcecode covbr output file
        @param [out]srcblocks: source code blocks after parse
        @retval True: success  False:fail
        """
        FH = file(self.file_path)
        source_str = FH.read()
        FH.close()
        source_str = re.sub("\n            ","",source_str) #remove wrap
        source_str = source_str.replace("\n","[newline]")
        source_str = re.sub("//.*?\[newline\]","[newline]",source_str) #remove comment //
        source_str = re.sub(r"/\s*\*.*?\*\s*/","",source_str) #remove comment /* */
        source_str = source_str.replace("[newline]","\n") #
        cur_pos = 0
        (self.source_path,pos) = self.__get_line(source_str[cur_pos:-1]);
        cur_pos += pos
        self.source_path = self.source_path.strip() #source code path
        #print self.source_path, cur_pos
        size = len(source_str)
        while cur_pos < size:
            ma = self.r.search(source_str[cur_pos:-1])
            if ma:
                if ma.group('flag') != "":
                    newblock = SrcBlock()
                    newblock.flag_str = ma.group('flag')
                    srcblocks.append(newblock)
                    newblock.start_line = int(ma.group('lineno'))
                    self.parseBlock(source_str[cur_pos+ma.end():-1],newblock)
                else:
                    pass
                cur_pos += ma.end()
            else:
                cur_pos += 1
                    
class SrcBlock(object):
    OTHERBLK = 1
    FUNBLK = 2
    IFBLK = 3
    FORBLK = 4
    ELSEIFBLK = 5
    ELSEBLK = 6
    WHILEBLK = 7
    SWITCHBLK = 8
    
    def __init__(self):
        self.block_type=SrcBlock.OTHERBLK
        self.start_line = -1
        self.end_line = 0
        self.excuted = False
        self.flag_str = ""
        self.conditions = []
    def __str__(self):
        return "block_type:%d,start_line:%d,end_line:%d,excuted:%d,flag:%s"%(self.block_type,self.start_line,self.end_line,self.excuted, self.flag_str)

def parse(input_path,output_path):
    #print input_path
    srcblks = []
    meta_file = MetaFile(input_path,output_path) 
    meta_file.parseSourceCovbr(srcblks)
    #for blk in srcblks:
    #    print str(blk)
    return srcblks

def isExecuted(lineno,srcblks):
    curblk = None
    for blk in srcblks:
        if lineno in range(blk.start_line,blk.end_line + 1):
            if curblk == None:
                curblk = blk
                continue
            curblkset = set(range(curblk.start_line,curblk.end_line + 1))
            blkset = set(range(blk.start_line,blk.end_line + 1))
            if blkset.issubset(curblkset):
                curblk = blk
    if curblk==None:
        return EXECUTED_IGNORE 
    if curblk.excuted==True:
        return EXECUTED_YES
    if curblk.excuted==False:
        if lineno==curblk.start_line and \
            (curblk.flag_str.find("F")>=0 or curblk.flag_str.find("f")>=0):
            return EXECUTED_YES 
    return EXECUTED_NO

help_message = '''
The help message goes here.
python incstatmentcov.py -s [source_dir] -d [svndiff_file] -c [covfile] 
                         -l [linenumber] -o [output]
-h help message
-s the file_path of source
-d the diff of two svn version
-c the cov_file
-o specify a output file, default is stdout
-l display the num of lines, default is 0
'''

def main(argv=None):
    if argv is None:
            argv = sys.argv
    
    try:    
        opts, args = getopt.getopt(argv[1:], "hs:vd:vc:vo:vl:v", ["help", "src=","diff=","cov=","output=","linecnt="])
    except getopt.error, msg:
        print help_message
        exit(1)

    src_path = None
    diff_file = None
    cov_file = None
    output_path = None
    linecnt = 0
    # option processing
    for option, value in opts:
        if option == "-v":
            verbose = "1.0.0"
            print verbose
            sys.exit(0)
        if option in ("-h", "--help"):
            print help_message
            exit(0)
        if option in ("-s", "--src"):
            src_path = value
        if option in ("-d", "--diff"):
            diff_file = value
        if option in ("-c", "--cov"):
            cov_file = value
        if option in ("-o", "--output"):
            output_path = value
        if option in ("-l", "--linecnt"):
            linecnt = int(value)
    #clear output file
    if output_path:
        os.system('> %s'% output_path)
    #fetch the diff code
    diff_result = {}
    code_diff(diff_file,diff_result) 
    modfun_result = {}
    modfun(diff_result,modfun_result) 
    #set the env cov
    os.putenv("COVFILE",cov_file)
    for key in modfun_result:
        abs_path = os.path.normpath('%s/%s'%(src_path,key))
        os.system('covbr -ar "%s" >"%s" 2>/dev/null' % (abs_path,abs_path+".br"))
        srcblks = parse(abs_path+'.br',abs_path+'.rs')
        executed_list = []
        nonexecuted_list = []
        ignore_list = []
        extra_set = set()
        for block in modfun_result[key]:
            a,b = block.get_start_end()
            #for blk in srcblks:
            #    print str(blk)
            for i in range(a,b+1):
                b_exe = isExecuted(i,srcblks)
                if b_exe==EXECUTED_YES:
                    executed_list.append(i)
                elif b_exe==EXECUTED_NO:
                    nonexecuted_list.append(i)
                else:
                    ignore_list.append(i)
    #deal with -l 
        if linecnt > 0:
            for lineno in executed_list:
                startno = lineno - linecnt
                if startno < 1:
                    startno = 1
                endno = lineno + linecnt
                if endno > len(linecache.getlines(abs_path))+1:
                    endno = len(linecache.getlines(abs_path))+1
                extra_set.update(set(range(startno,endno+1)))
            for lineno in nonexecuted_list:
                startno = lineno - linecnt
                if startno < 1:
                    startno = 1
                endno = lineno + linecnt
                if endno > len(linecache.getlines(abs_path))+1:
                    endno = len(linecache.getlines(abs_path))+1
                extra_set.update(set(range(startno,endno+1)))
            extra_set.difference_update(set(executed_list))
            extra_set.difference_update(set(nonexecuted_list))
        stdout_bak = sys.stdout
        if output_path:
            f = open(output_path, 'a')
            sys.stdout = f
            print >>f,"\n",abs_path
        else:
            print "###############################################\n",abs_path
        #print diff lines
        for i in range(1,len(linecache.getlines(abs_path))+2):
            color_mode = TTY_CLEAR
            needprint = False
            if i in executed_list:
                color_mode = TTY_GREEN
                needprint = True
            elif i in nonexecuted_list:
                color_mode = TTY_RED
                needprint = True
            elif i in extra_set:
                color_mode = TTY_CLEAR
                needprint = True
            elif i in ignore_list:
                color_mode = TTY_BLUE
                needprint = True
            if needprint:
                if not output_path:
                    line = linecache.getline(abs_path, i).strip('\n')
                    pretty_print(color_mode,"%5d:" % i,False)
                    pretty_print(color_mode,line)
                else:
                    line = linecache.getline(abs_path, i).strip('\n')
                    file_print(color_mode,"%5d: %s" %(i,line))
        if output_path:
            f.close()
        linecache.clearcache()
        sys.stdout = stdout_bak
        os.system('rm -rf "%s" "%s"' % (abs_path+".br",abs_path+".rs"))
                        
if __name__ == "__main__":
    sys.exit(main()) 
