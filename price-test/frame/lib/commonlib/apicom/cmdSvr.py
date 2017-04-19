# -*- coding: gb2312 -*- 

'''
CmdServer模块
@authors  :   U{xieping<mailto: xieping>}
@copyright:   
@date     :   2009-09-21
@version  :   1.0.0.0
'''

import os;
import re;
import sys;
import glob;
import getopt;
import signal;
import commands;

import share;

MAX_PIPE_BUF = 10240;
WRITE_SIZE = 0;

def run(cmdSvrRecv,cmdSvrSend):
    global WRITE_SIZE,MAX_PIPE_BUF;
    while True:
        cmd = os.read(cmdSvrRecv,MAX_PIPE_BUF);
        output = commands.getstatusoutput( cmd );	 

        WRITE_SIZE = len(str(output[0])) + 1 + len(output[1]);
        os.write(cmdSvrSend,str(output[0]) + '\n' + output[1]);        

def execute(cmd,outputFlag=True):
    if outputFlag:
        print 'Execute command:',cmd;

    global WRITE_SIZE,MAX_PIPE_BUF;
    clientSend = share.clientSend;
    clientRecv = share.clientRecv;
    os.write(clientSend,cmd);

    outBuf = os.read(clientRecv,MAX_PIPE_BUF);

    outBufList = outBuf.split('\n',1);
    if outputFlag:
        print 'Command excute result code:',outBufList[0];
        print outBufList[1],'\n';

    return int(outBufList[0]),outBufList[1];
    
