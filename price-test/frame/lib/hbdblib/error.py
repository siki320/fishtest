# -*- coding: GB18030 -*-
"""
@author: maqi
@copyright: Copyright (c) 2011 XX, Inc. All Rights Reserved
"""

class HBDBError(Exception):
    '''base class for hbdb exceptions'''
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

    def __repr__(self):
        return 'HBDB Error : ' + self.msg

