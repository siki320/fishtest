# -*- coding: GB18030 -*-
'''
Created on Nov 16, 2011

@author: caiyifeng<caiyifeng>

@summary: �������·��
'''

import os
import sys
import itertools

def get_relpath(abspath):
    '''
    @summary: ��abspath�����·��
    @note: ȥ��abspath��sys.path[0](���ű�·��)�Ĺ�ͬǰ׺
    '''
    abspath = os.path.abspath(abspath)
    mainpath = os.path.abspath(sys.path[0])
    
    common, (relpath, nouse) = _common_prefix(abspath.split("/"), mainpath.split("/"))
    relpath = "/".join(relpath)
    
    # ȥ��ͷ�ϵ�'/'��ȷ����һ�����·��
    return relpath.lstrip("/")

    
def _all_equal(elements):
    '''
    @summary: return True if all the elements are equal, otherwise False
    @author: <Python Cookbook 2.22>
    ''' 
    first_element = elements[0]
    
    for other_element in elements[1:]: 
        if other_element != first_element: 
            return False
        
    return True

def _common_prefix(*sequences):
    '''
    @summary: 
     - return a list of common elements at the start of all sequences
     - then a list of lists that are the unique tails of each sequence
    @author: <Python Cookbook 2.22>
    '''
    # if there are no sequences at all, we're done
    if not sequences: 
        return [ ], [ ]
    
    # loop in parallel on the sequences 
    common = [ ]
    for elements in itertools.izip(*sequences): 
        # unless all elements are equal, bail out of the loop 
        if not _all_equal(elements): 
            break 
        # got one more common element, append it and keep looping 
        common.append(elements[0])
        
    # return the common prefix and unique tails 
    return common, [ sequence[len(common):] for sequence in sequences ]

