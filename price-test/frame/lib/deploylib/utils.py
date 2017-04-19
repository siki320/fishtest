# -*- coding: GB18030 -*-
"""
@author: maqi
@date: Feb 2, 2011
@summary: dts deploy 工具集
@version: 1.0.0.0
@copyright: Copyright (c) 2011 XX, Inc. All Rights Reserved
"""

import socket

healthy_clients_list=[]

def ping(ip,port,timeout=5):
    try:
        if healthy_clients_list.count(ip) == 0:
            cs=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            address=(str(ip),int(port))
            cs.settimeout(timeout)
            status = cs.connect_ex((address))
            if status != 0:
                return 1
            else:
                healthy_clients_list.append(ip)
                return 0
    except Exception ,e:
        print "error:%s" %e
        return 1
    return 0

def get_free_port():
    """attempts to find a free port"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("localhost", 0))
    _, port = s.getsockname()
    s.close()
    return port
