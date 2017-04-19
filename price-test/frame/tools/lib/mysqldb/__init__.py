import os, sys
from ctypes import cdll
current_path = os.path.abspath( os.path.dirname(__file__) )
cdll.LoadLibrary(current_path+"/libmysqlclient_r.so")
if current_path not in sys.path:
    sys.path.append(current_path)
