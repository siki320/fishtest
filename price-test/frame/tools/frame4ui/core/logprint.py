#/***************************************************************************
# *
# * Copyright (c) 2010 XX, Inc. All Rights Reserved
# *
# **************************************************************************/
#/**
# * @author yangming03
# * @date 2012/11/26
# * @version $Revision: 1.0
# *
# **/
import sys, os, traceback, string
from datetime import datetime

class Logger(object):
	logger = None
	def __init__(self, filename):
		self.levelIndex = {'output': 1 , 'prompt':2 , 'exception':3, 'error':4, 'warning':5, 'info':6, 'debug':7, 'trace':8}
		self.logLevel = 'trace'
		self.dispLevel = 'output'

		dateTime = str(datetime.now())
		self.timeStamp = "%s-%s-%s-%s-%s"%(dateTime[:10],dateTime[11:13],dateTime[14:16],dateTime[17:19],dateTime[20:])
		self.log_Path = os.path.join(os.getcwd(),"logs")
		self.logPath = os.path.join(self.log_Path,self.timeStamp)
		if not os.path.exists(self.log_Path):
				os.mkdir(self.log_Path)
		if not os.path.exists(self.logPath):
				os.mkdir(self.logPath)
		self.logFile = open (os.path.join(self.logPath, filename), "w")
		self.fileName = self.logFile.name

		self.outputStack = DTS_Stack()
		self.exceptionStack = DTS_Stack()
		self.errorStack = DTS_Stack()
		self.warningStack =DTS_Stack()
		self.infoStack = DTS_Stack()
		self.debugStack = DTS_Stack()
		self.traceStack = DTS_Stack()

	def initialize(file):
		Logger.logger = Logger( file )
	initialize = staticmethod(initialize)

	def isInitialed():
		return Logger.logger != None
	isInitialed = staticmethod(isInitialed)
	
	def shutdown():
		Logger.logger.__shutdown()
	shutdown = staticmethod(shutdown)

	def getLogPath():
		return Logger.logger.logPath
	getLogPath = staticmethod(getLogPath)

	def output(msg,  target = 'output', lineChange = True):
		Logger.logger.__output(msg, target, lineChange)
	output = staticmethod(output)

	def exception(exception):
		Logger.logger.__exception(exception)
	exception = staticmethod(exception)

	def error(msg):
		Logger.logger.__error(msg)
	error = staticmethod(error)

	def warning(msg):
		Logger.logger.__warning(msg)
	warning = staticmethod(warning)

	def info(msg):
		Logger.logger.__info(msg)
	info = staticmethod(info)

	def debug(msg):
		Logger.logger.__debug(msg)
	debug = staticmethod(debug)

	def trace():
		Logger.logger.__trace()
	trace = staticmethod(trace)

	def pushSection(section):
		Logger.logger.__pushSection(section)
	pushSection = staticmethod(pushSection)

	def popSection():
		Logger.logger.__popSection()
	popSection = staticmethod(popSection)

	def __shutdown(self):
		self.logFile.close()

	def __output(self, msg, target = 'output', lineChange = True):
		if 'prompt' == target:
			self.safeWrite(msg, "PROMPT")
		else:
			if lineChange:
				print msg
			else:
				print msg,
			self.safeWrite(msg, "OUTPUT")

	def __exception(self, exception):
		msg = traceback.format_exc().strip()
		self.safeWrite(msg, "EXCEPTION")

	def __error(self, msg):
		self.safeWrite(msg, "ERROR")

	def __warning(self, msg):
		self.safeWrite(msg, "WARNING")

	def __info(self, msg):
		self.safeWrite(msg, "INFO")

	def __debug(self, msg):
		self.safeWrite(msg, "DEBUG")

	def __trace( self ):
		msg = " <= ".join( [ "%s,%s,%s"%( os.path.basename( item[ 0 ] ),
										  item[ 2 ], item[ 1 ] )
							 for item in reversed( traceback.extract_stack()[ :-2 ] )
			     ] )
		self.safeWrite(msg, "TRACE")

	def getpath( self ):
		return self.logPath

	def safeWrite(self, msg, level):
		try:
			if self.levelIndex[self.dispLevel.lower()] >= self.levelIndex[level.lower()]:
				if 'output' != level.lower() and 'prompt' != level.lower():
					print level + " : " +msg
			if self.levelIndex[self.logLevel.lower()] >= self.levelIndex[level.lower()]:
				timeStamp = datetime.now().isoformat()
				logMessage = level + " : " + timeStamp + " : "	+ msg + "\n"
				self.logFile.write(logMessage)
				self.logFile.flush()
		except KeyError:
				errmsg = "Logger.safeWrite() key error. Should never get here"
				print errmsg
				timeStamp = datetime.now().isoformat()
				logMessage = level + " : " + timeStamp + " : "	+ errmsg + "\n"
				self.logFile.write(logMessage)
				self.logFile.flush()

class DTS_Stack:
	def __init__(self):
		self.stack = []
	def push(self, section):
	    self.stack.append(section)
	def pop(self):
	    if len(self.stack) == 0:
	        raise "Error", "stack is empty"
	    return self.stack.pop()
	def isEmpty(self):
	    if len(self.stack) == 0:
	        return 1
	    return 0
	def numOfElements(self):
	    return len(self.stack)
	def dumpStack(self):
		n = len(self.stack)
		fmt = "  %%%dd  %%s" % len(`n + 1`)
		for i in xrange(n):
			print fmt % (n - i, self.stack[i])


if __name__ == "__main__":
	Logger.initialize("Main.log")

