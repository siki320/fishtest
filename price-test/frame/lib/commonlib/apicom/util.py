# -*- coding: gb2312 -*- 
import time;
import struct;
import socket;
import random;

ISOTIMEFORMAT='%Y-%m-%d %X';

def getStrTime(t):
    return time.strftime(ISOTIMEFORMAT, time.localtime(int(t)));

def getIntTime(s):
    return int(time.mktime(time.strptime(s,ISOTIMEFORMAT)));

#ip :str
def ip2str(ip):    
    return str(struct.unpack("<I",socket.inet_aton(ip))[0]);

#s :str
def str2ip(s):
    return str(socket.inet_ntoa(struct.pack("<I",int(s))));

def longStr2Twoint(s):
    return struct.unpack("ii", s) 

def Twoint2longStr(a,b):
    return struct.pack("ii", a, b);

def byte2hex(s):
    return ''.join( [ "%02x " % ord( x ) for x in s ] ).strip();

def hex2byte(hexStr):
    bytes=[];
    hexStr = ''.join(hexStr.split(' '));
    for i in range(0,len(hexStr),2):
        bytes.append(chr(int(hexStr[i:i+2],16)));

    return ''.join(bytes);
