# -*- coding: gb2312 -*- 

'''
缺省的接收协议
@authors  :   U{xieping<mailto: xieping>}
@copyright:   
@date     :   2009-09-1
@version  :   1.0.0.0
'''

from netlib.netlib import Server;
from netlib.netlib import Client;
from frame.lib.commonlib.apicom.exception import *

import struct;

'''
@newfield desc: Description
'''

def getSeProtocolData(mock,s,headLen = 4, bodyOffset=0,bodyOffsetSize=4,bsbcacFlag=False):
    flag = 'I';
    if(bodyOffsetSize == 1):
        flag = 'B';
    elif(bodyOffsetSize == 2):
        flag = 'H';
    elif(bodyOffsetSize == 3):
        flag = 'BBB';        
    elif(bodyOffsetSize == 4):
        flag = 'I';
    elif(bodyOffsetSize == 5):
        flag = 'BBBBB';
    elif(bodyOffsetSize == 6):
        flag = 'BBBBBB';
    elif(bodyOffsetSize == 7):
        flag = 'BBBBBBB';
    elif(bodyOffsetSize == 8):
        flag = 'L';        
    else:
        raise BaseException,"The bodyOffsetSize:%d is not supported" %(bodyOffsetSize,);

    format = str(bodyOffset) + 'x ' + str(bodyOffsetSize) + 's ' + str(headLen - bodyOffset - bodyOffsetSize) + 'x'; 
          
    if isinstance (mock, Server):
        buf1 = mock.recv(s,headLen);
            
        bodyLenBuf = struct.unpack(format,buf1)[0];
        bodyLenList = struct.unpack('<' + flag,bodyLenBuf); #the bodyLen is little-endian
        bodyLen = 0;
        if flag == 'B' or flag == 'H' or flag == 'I' or flag == 'L':
            bodyLen = bodyLenList[0];
            if flag == 'I' and bsbcacFlag:
                bodyLen = ((bodyLen & 0xFFFF0000)>>16) + ((bodyLen & 0xFF)<<16);
        elif flag == 'BBB': #flag 3
            for i in range(2,-1,-1):
                bodyLen = bodyLenList[i] + bodyLen * 256;
        elif flag == 'BBBBB': #flag 5
            for i in range(4,-1,-1):
                bodyLen = bodyLenList[i] + bodyLen * 256;
        elif flag == 'BBBBBB': #flag 6
            for i in range(5,-1,-1):
                bodyLen = bodyLenList[i] + bodyLen * 256;
        elif flag == 'BBBBBBB': #flag 7
            for i in range(6,-1,-1):
                bodyLen = bodyLenList[i] + bodyLen * 256;

        buf2 = mock.recv(s,bodyLen);
            
        return ''.join([buf1 ,buf2]);  
    elif isinstance (mock, Client):
        buf1 = mock.recv(headLen);
    
        bodyLenBuf = struct.unpack(format,buf1)[0];
        bodyLen = struct.unpack('<' + flag,bodyLenBuf)[0];#the bodyLen is little-endian

        buf2 = mock.recv(bodyLen);

        return ''.join([buf1 ,buf2]);        


