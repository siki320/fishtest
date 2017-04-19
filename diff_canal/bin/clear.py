import os,sys,subprocess,json
import re
import redis
reload(sys)
sys.setdefaultencoding('utf-8')
if os.path.exists(os.path.realpath(sys.path[0]) + "/../lib"):
	sys.path.append(os.path.realpath(sys.path[0]) + "/../lib")
else:
	sys.path.append(os.path.realpath(sys.path[0]) + "lib")
import logging
import memcache
import random, datetime
from Configuration import CONSOLE_LOGGING_ONLY
from ConfReader import *

if CONSOLE_LOGGING_ONLY:
    logging.basicConfig(
            level = logging.DEBUG,
            format = '[%(asctime)s] [%(filename)s (line:%(lineno)d)] [%(levelname)s] [%(message)s]',
            datefmt = '%a, %d %b %Y %H:%M:%S')
else:
    logging.basicConfig(
            level = logging.DEBUG,
            filename = os.path.join(os.path.realpath(sys.path[0]), '../log/ClearDataIdCKV.log'),
            format = '[%(asctime)s] [%(filename)s (line:%(lineno)d)] [%(levelname)s] [%(message)s]',
            datefmt = '%a, %d %b %Y %H:%M:%S')

#Read config
if len(sys.argv)==1:
	cfg_dic=ReadServerConf()
else:
	cfg_dic=ReadServerConf(sys.argv[1])

#double config
mc_conn0="%s:%s" % (mc_host0, mc_port0)
id_host0=cfg_dic["redis0"]["rds_host"]
id_host1=cfg_dic["redis1"]["rds_host"]
id_port0=cfg_dic["redis0"]["rds_port"]
id_port1=cfg_dic["redis1"]["rds_port"]
#Create memcache/redis connection
mc0 = memcache.Client([mc_conn0], debug=0)
r0 = redis.Redis(id_host0,id_port0)
r1 = redis.Redis(id_host1,id_port1)


logging.info("clear old data in redis.")

try:
    r0.flushdb()
    r1.flushdb()


except IOError as err:
    logging.warning("Failed to clear redis: %s" % str(err))
    sys.exit(1)

time.sleep(3)
logging.info("clear all data in redis."),