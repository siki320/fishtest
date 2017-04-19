#!/usr/bin/python
# -*- coding: GB18030 -*-

from frame.tools.cov.ply import lex as lex
from frame.tools.cov.svndiff import CodeBlock, SvnDiff 
from frame.lib.commonlib.dtssystem import dtssystem
import os
import sys
import re

import inspect

def lineno():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno

version = __version__ = "2.2"

keywords = [
    'if',
    'else',
    'switch',
    'case',
]

tokens = [
    'NUMBER',
    'CHAR_LITERAL',
    'NAME',
    'OPEN_PAREN',
    'CLOSE_PAREN',
    'OPEN_BRACE',
    'CLOSE_BRACE',
    'OPEN_SQUARE_BRACKET',
    'CLOSE_SQUARE_BRACKET',
    'COLONCOLON',
    'COLON',
    'SEMI_COLON',
    'COMMA',
    'TAB',
    'BACKSLASH',
    'PIPE',
    'PERCENT',
    'EXCLAMATION',
    'CARET',
    'COMMENT_SINGLELINE',
    'COMMENT_MULTILINE',
    'PRECOMP_MACRO',
#    'PRECOMP_MACRO_CONT',
    'ASTERISK',
    'AMPERSTAND',
    'EQUALS',
    'MINUS',
    'PLUS',
    'DIVIDE',
    #'CHAR_LITERAL',
    'STRING_LITERAL',
    'NEW_LINE',
]

t_ignore = " \r.?@$"
t_NUMBER = r'[0-9][0-9XxA-Fa-f]*'
t_NAME = r'[<>A-Za-z_~][A-Za-z0-9_]*'
t_OPEN_PAREN = r'\('
t_CLOSE_PAREN = r'\)'
t_OPEN_BRACE = r'{'
t_CLOSE_BRACE = r'}'
t_OPEN_SQUARE_BRACKET = r'\['
t_CLOSE_SQUARE_BRACKET = r'\]'
t_SEMI_COLON = r';'
t_COLONCOLON = r'::'
t_COLON = r':'
t_COMMA = r','
t_TAB = r'\t'
t_BACKSLASH = r'\\'
t_PIPE = r'\|'
t_PERCENT = r'%'
t_CARET = r'\^'
t_EXCLAMATION = r'!'

def t_PRECOMP_MACRO(t):
    r'\#.*'
    t.lexer.lineno += t.value.count("\n")
    return t
"""
def t_PRECOMP_MACRO_CONT(t):
    r'.*\\\n'
    t.lexer.lineno += 1
    return t
"""

def t_COMMENT_SINGLELINE(t):
    r'\/\/.*\n'
    t.lexer.lineno += 1
    global doxygenCommentCache
    if t.value.startswith("///") or t.value.startswith("//!"):
        if doxygenCommentCache:
            doxygenCommentCache += "\n"
        if t.value.endswith("\n"):
            doxygenCommentCache += t.value[:-1]
        else:
            doxygenCommentCache += t.value
    return t

t_ASTERISK = r'\*'
t_MINUS = r'\-'
t_PLUS = r'\+'
t_DIVIDE = r'/[^/]'
t_AMPERSTAND = r'&'
t_EQUALS = r'='
t_CHAR_LITERAL = r"'\\?.'"

#found at http://wordaligned.org/articles/string-literals-and-regular-expressions
#TODO: This does not work with the string "bla \" bla"

def t_STRING_LITERAL(t):
    r'"(.|[\r\n])*?[^\\]?"'
    t.lexer.lineno += t.value.count("\n")
    #print "STRING:===%s====="%t.value
    return t

#Found at http://ostermiller.org/findcomment.html
def t_COMMENT_MULTILINE(t):
    r'/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/'
    t.lexer.lineno += t.value.count("\n")
    global doxygenCommentCache
    if t.value.startswith("/**") or t.value.startswith("/*!"):
        #not sure why, but get double idl lines
        v = t.value.replace("\n\n", "\n")
        #strip prefixing whitespace
        v = re.sub("\n[\s]+\*", "\n*", v)
        doxygenCommentCache += v
    return t

def t_NEW_LINE(t):
    r'\n'
    t.lexer.lineno += 1
    return t

def t_error(v):
    print(( "Lex error: ", v ))

#lex.lex()
# Controls error_print
print_errors = 1
# Controls warning_print
print_warnings = 1
# Controls debug_print
debug = 0
# Controls trace_print
debug_trace = 0

def error_print(arg):
    if print_errors: print("[%4d] %s"%(inspect.currentframe().f_back.f_lineno, arg))

def warning_print(arg):
    if print_warnings: print("[%4d] %s"%(inspect.currentframe().f_back.f_lineno, arg))

def debug_print(arg):
    global debug
    if debug: print("[%4d] %s"%(inspect.currentframe().f_back.f_lineno, arg))

def trace_print(*arg):
    global debug_trace
    if debug_trace:
        sys.stdout.write("[%s] "%(inspect.currentframe().f_back.f_lineno))
        for a in arg: sys.stdout.write("%s "%a)
        sys.stdout.write("\n")

doxygenCommentCache = ""

#Track what was added in what order and at what depth
parseHistory = []

class FunctionObj(object):
    def __init__(self):
        self.name = ""
        self.startline = -1
        self.endline = -1
    def __str__(self):
        return "%s,%d,%d"%(self.name,self.startline,self.endline)

class CppSource(object):

    def __init__(self, sourceFileName, argType="file", **kwargs):
        """Create the parsed C++ source file parse tree
        
        sourceFileName - Name of the file to parse OR actual file contents (depends on argType)
        argType - Indicates how to interpret sourceFileName as a file string or file name
        kwargs - Supports the following keywords
        """
        ## reset global state ##
        global doxygenCommentCache
        doxygenCommentCache = ""

        if (argType == "file"):
            self.sourceFileName = os.path.expandvars(sourceFileName)
            self.mainClass = os.path.split(self.sourceFileName)[1][:-3]
            sourceFileStr = ""
        elif argType == "string":
            self.sourceFileName = ""
            self.mainClass = "???"
            sourceFileStr = sourceFileName
        else:
            raise Exception("Arg type must be either file or string")
        self.curClass = ""
       
        self.functions = []

        if (len(self.sourceFileName)):
            fd = open(self.sourceFileName)
            sourceFileStr = "".join(fd.readlines())
            fd.close()     
        
        # Make sure supportedAccessSpecifier are sane
        
        self.braceDepth = 0
        lex.lex()
        lex.input(sourceFileStr)
        curLine = 0
        curChar = 0
        function_name=""
        self.nameStack = []
        self.openParenStack = []
        self.closeParenStack = []
        self.openBraceStack = []
        self.closeBraceStack = []
        self.classstack = []
        self.openBraceStackClass = []
        self.closeBraceStackClass = []
        self.paramStack = []
        self.namespace = ""
        while True:
            tok = lex.token()
            if not tok: break
            curLine = tok.lineno
            curChar = tok.lexpos
            if tok.type == 'NAME':
                if tok.value in keywords:
                    continue
                if len(self.openParenStack)>len(self.closeParenStack):
                    continue
                self.nameStack.append(tok)

            elif tok.type == 'SEMI_COLON':
                self.nameStack = []
                self.openParenStack = []
                self.closeParenStack = []
                self.namespace = ""

            elif tok.type == 'OPEN_BRACE':
                if len(self.nameStack)>=2 and self.nameStack[-2].value=="class":
                    #class named的情况下
                    classname = self.nameStack[-1].value
                    if len(self.classstack)>0: #如果有class，将class的大括号入栈
                        self.openBraceStackClass.append(tok)
                    self.classstack.append(classname)
                    self.openBraceStackClass = [] #只有一个class
                    self.closeBraceStackClass = []
                    self.openBraceStackClass.append(tok)
                    continue

                if len(self.nameStack)>=2 and len(self.openParenStack)==1\
                        and len(self.closeParenStack)==1: #函数的情况
                    #只有函数名的情况
                    function_name = self.nameStack[-1].value
                    self.openBraceStack = []
                    self.closeBraceStack = []
                    self.openBraceStack.append(tok)
                    if function_name == "const":
                        function_name = self.nameStack[-2].value
                    if self.namespace != "":
                        function_name = self.namespace+"::"+function_name
                    elif len(self.classstack)>0:
                        function_name = self.classstack[-1]+"::"+function_name
                    fo = FunctionObj()
                    fo.name = function_name
                    fo.startline = tok.lineno
                    self.functions.append(fo)
                    self.nameStack = []
                    self.openParenStack = []
                    self.closeParenStack = []
                    continue

                self.openBraceStack.append(tok)

                self.nameStack = []
                self.namespace = ""

            elif tok.type == 'CLOSE_BRACE':
                self.closeBraceStack.append(tok)
                self.closeBraceStackClass.append(tok)
                if len(self.closeBraceStack) == len(self.openBraceStack):
                    if function_name:
                        self.functions[-1].endline = tok.lineno
                        function_name = ""
                if len(self.closeBraceStackClass) == len(self.openBraceStackClass):
                    self.classname = ""
                self.namespace = ""

            elif tok.type == 'OPEN_PAREN':
                self.openParenStack.append(tok) 
            elif tok.type == 'CLOSE_PAREN':
                pos = 0
                if len(self.openParenStack)>0:
                    pos = self.openParenStack[-1].lexpos
                temp = []
                temp.extend(self.nameStack) 
                for idx in range(len(temp)):
                    tt = temp[idx]
                    if tt.lexpos>pos:
                        self.nameStack.remove(tt)
                self.closeParenStack.append(tok) 
            elif tok.type == 'COLONCOLON':
                if len(self.openParenStack)>len(self.closeParenStack):
                    continue
                if len(self.nameStack)>0:
                    self.namespace = self.nameStack[-1].value
            else:
                pass
    def printFunctions(self):
        for f in self.functions:
            print f 

def parse_cppfile(cppfile):
    functions = []
    if not os.path.exists(cppfile): 
        raise Exception,"can not open file:%s"%(cppfile)
    func_stat_path = os.path.dirname(os.path.abspath(__file__))
    (ret,output,err)=dtssystem('cat %s | %s/func_stat '%(cppfile,func_stat_path), output=True)
    lines = output.split("\n")
    for line in lines:
        if line=="":
            continue
        temp = line.split("\t")
        fo = FunctionObj()
        fo.name = temp[0]
        fo.startline = int(temp[1])
        fo.endline = int(temp[2])
        functions.append(fo)
    return functions

def getDiffFuncList(src_path, svndiff):
    functionlist = []
    result={}
    tmp_svn=SvnDiff(svndiff,result,src_path)
    tmp_svn.code_diff()
    for srcfile in result.keys():
        print src_path+"/"+srcfile
        try:
            cppParser=CppSource(src_path+"/"+srcfile)
        except:
            print "%s:process error"%srcfile
            continue
        for f in cppParser.functions:
            for diffb in result[srcfile]: 
                if f.startline<=diffb.startline and f.endline>=diffb.startline:
                    functionlist.append(f.name)
                    break
                if f.endline>=diffb.endline and f.startline<=diffb.endline:
                    functionlist.append(f.name)
                    break
    return functionlist

def getDiffFuncList2(src_path, svndiff):
    functionlist = []
    result={}
    tmp_svn=SvnDiff(svndiff,result,src_path)
    tmp_svn.code_diff()
    for srcfile in result.keys():
        #print src_path+"/"+srcfile
        try:
            functions=parse_cppfile(src_path+"/"+srcfile)
        except:
            print "%s:process error"%srcfile
            continue
        for f in functions:
            for diffb in result[srcfile]:
                if f.startline<=diffb.startline and f.endline>=diffb.startline:
                    functionlist.append(f.name)
                    break
                if f.endline>=diffb.endline and f.startline<=diffb.endline:
                    functionlist.append(f.name)
                    break
    return functionlist

if __name__ == '__main__':
    for cppfile in sys.argv[1:]:
        print "process begin %s"%cppfile
        if True:
            functions=parse_cppfile(cppfile)
        else:
            cppParser=CppSource(cppfile)
            functions=cppParser.functions
            
        for f in functions:
            print f
        print "process end %s"%cppfile
    #print getDiffFuncList("../","../run_env/svn_diff.txt")
