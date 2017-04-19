# This file was created automatically by SWIG.
# Don't modify this file, modify the SWIG interface instead.
# This file is compatible with both classic and idl-style classes.

import _pybft

def _swig_setattr(self,class_type,name,value):
    if (name == "this"):
        if isinstance(value, class_type):
            self.__dict__[name] = value.this
            if hasattr(value,"thisown"): self.__dict__["thisown"] = value.thisown
            del value.thisown
            return
    method = class_type.__swig_setmethods__.get(name,None)
    if method: return method(self,value)
    self.__dict__[name] = value

def _swig_getattr(self,class_type,name):
    method = class_type.__swig_getmethods__.get(name,None)
    if method: return method(self)
    raise AttributeError,name

import types
try:
    _object = types.ObjectType
    _newclass = 1
except AttributeError:
    class _object : pass
    _newclass = 0
del types


MAX_BUF_SIZE = _pybft.MAX_BUF_SIZE
MAX_ERROR_BUF_SIZE = _pybft.MAX_ERROR_BUF_SIZE

init_log = _pybft.init_log

set_bftLogPath = _pybft.set_bftLogPath

open_bft_log = _pybft.open_bft_log
class CBFT(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, CBFT, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, CBFT, name)
    def __repr__(self):
        return "<C CBFT instance at %s>" % (self.this,)
    __swig_setmethods__["instance"] = _pybft.CBFT_instance_set
    __swig_getmethods__["instance"] = _pybft.CBFT_instance_get
    if _newclass:instance = property(_pybft.CBFT_instance_get, _pybft.CBFT_instance_set)
    def __init__(self, *args):
        _swig_setattr(self, CBFT, 'this', _pybft.new_CBFT(*args))
        _swig_setattr(self, CBFT, 'thisown', 1)
    def __del__(self, destroy=_pybft.delete_CBFT):
        try:
            if self.thisown: destroy(self)
        except: pass
    def load_template(*args): return _pybft.CBFT_load_template(*args)
    def load_data(*args): return _pybft.CBFT_load_data(*args)
    def dump_data(*args): return _pybft.CBFT_dump_data(*args)
    def next(*args): return _pybft.CBFT_next(*args)
    def export_bin(*args): return _pybft.CBFT_export_bin(*args)
    def import_bin(*args): return _pybft.CBFT_import_bin(*args)
    def export_json(*args): return _pybft.CBFT_export_json(*args)
    def import_json(*args): return _pybft.CBFT_import_json(*args)
    def length(*args): return _pybft.CBFT_length(*args)
    def option_on(*args): return _pybft.CBFT_option_on(*args)
    def option_off(*args): return _pybft.CBFT_option_off(*args)
    def alias(*args): return _pybft.CBFT_alias(*args)
    def get(*args): return _pybft.CBFT_get(*args)
    def set(*args): return _pybft.CBFT_set(*args)
    def dset(*args): return _pybft.CBFT_dset(*args)
    def size_of(*args): return _pybft.CBFT_size_of(*args)
    def list(*args): return _pybft.CBFT_list(*args)
    def listall(*args): return _pybft.CBFT_listall(*args)
    def list2buf(*args): return _pybft.CBFT_list2buf(*args)
    def listall2buf(*args): return _pybft.CBFT_listall2buf(*args)
    def hasKey(*args): return _pybft.CBFT_hasKey(*args)
    def get_undelete_node(*args): return _pybft.CBFT_get_undelete_node(*args)
    def get_undelete_var(*args): return _pybft.CBFT_get_undelete_var(*args)
    def clear(*args): return _pybft.CBFT_clear(*args)

class CBFTPtr(CBFT):
    def __init__(self, this):
        _swig_setattr(self, CBFT, 'this', this)
        if not hasattr(self,"thisown"): _swig_setattr(self, CBFT, 'thisown', 0)
        _swig_setattr(self, CBFT,self.__class__,CBFT)
_pybft.CBFT_swigregister(CBFTPtr)
cvar = _pybft.cvar


