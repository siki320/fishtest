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
import glob
import os
from logprint import Logger

class Casesinfo(object):
	def __init__(self, context):
		self.context = context
	        
	def showAllTestPlans(self,Path="DTS"):
		rawPlanList = []
		self.currentPath = "%s/*"%Path
		files = glob.glob(self.currentPath)
		for file in files:
			modulename, ext = os.path.splitext(self.getPlanName(file))
			if ext == ".pyc" or modulename == "__init__":
				pass
			elif os.path.isfile(file) and (not file.endswith(".py")):
				pass
			else:
				rawPlanList.append([self.getPlanName(file), self.getTime(file), self.getcaseNumber(file), self.getcaseStatus(file),file])

		sortedPlans = sorted(rawPlanList)
		retList = []
		retList.append(["Index", "Test Plan Name","Author", "Estimated Time(s)" ,"Cases Numbers" ,"Status"])
		index = 1
		for plan in sortedPlans:
			retList.append([index, plan[0], "yangming03",plan[1], plan[2],plan[3]])
			index = index + 1
		self.context.setPlanList(sortedPlans)
		return retList
	def getcaseStatus(self,file):
		key=file
		while file!="DTS":
			temp_return = self._getcaseStatus(file,key)
			if temp_return != "N/A":
				return temp_return
			pos= file.rfind("/")
                	temp_file=file[:pos]
			file=temp_file
		return 
			
	def _getcaseStatus(self, file,key):
		pos= file.rfind("/")
                caseInfofile =file[:pos]+"/.caseinfo"
		if os.path.isfile(caseInfofile):
                	tempcaseFile =open(caseInfofile,'r')
                	caseInfoLine = tempcaseFile.readline()
			if os.path.isfile(key):
                        	while caseInfoLine:
					params=caseInfoLine.split('\t')
                                	if params[0]==key:
						if params[1]=='P':
							return "Pass"
						else:
							return params[1]
					else:
						caseInfoLine = tempcaseFile.readline()
			elif os.path.isdir(key):
				while caseInfoLine:
                                        params=caseInfoLine.split('\t')
                                        if params[0]==key:
						return params[3]
                                        else:
                                                caseInfoLine = tempcaseFile.readline()
			else:
				return "N/A"
                else:
			return "N/A"
		return "N/A"
        def getcaseNumber(self,file):
		key=file
                while file!="DTS":
			temp_return=self._getcaseNumber(file,key)
			if temp_return != "N/A":
				return temp_return
                        pos= file.rfind("/")
                        temp_file=file[:pos]
                        file=temp_file
		return "N/A"

	def _getcaseNumber(self, file,key):
		casenumber=1
		clac_casenumber=0
		if os.path.isfile(file):
			return casenumber
		elif os.path.isdir(file):
			pos= file.rfind("/")
                	caseInfofile =file[:pos]+"/.caseinfo"
                	if os.path.isfile(caseInfofile):
				tempcaseFile =open(caseInfofile,'r')
                        	caseInfoLine = tempcaseFile.readline()
				while caseInfoLine:
                               		params=caseInfoLine.split('\t')
					if params[0]==key:
						casenumber = params[3].split('/')[2].split('\n')[0]
						return casenumber
					elif params[0].startswith(key):
						clac_casenumber += 1
						caseInfoLine = tempcaseFile.readline()
					else:
						caseInfoLine = tempcaseFile.readline()
				return clac_casenumber
		else:
			print "the file no exists::",file
			return "N/A"
		return "N/A"
					
					
	def getPlanName(self, file):
		name = ''
		if file !=None:
			name = file.rsplit('/',1)[1]
		#	if name !=None:
		#		name = name.split('.')[0]
		#if os.path.isfile(arg) and ext == ".py" and modulename != "__init__":
		return name

        def getTime(self,file):
		key = file
                while file!="DTS":
			temp_return=self._getTime(file,key)
			if temp_return != "N/A":
				return temp_return
                        pos= file.rfind("/")
                        temp_file=file[:pos]
                        file=temp_file
		return "N/A"

	def _getTime(self, file,key):
		pos = file.rfind("/")			
		caseInfofile =file[:pos]+"/.caseinfo"
		if os.path.isfile(caseInfofile):
			tempcaseFile =open(caseInfofile,'r')
			caseInfoLine = tempcaseFile.readline()
                	while caseInfoLine:
				params=caseInfoLine.split('\t')
                        	if key==params[0]:
					ms_time=params[2]
					return int(ms_time)/1000.0
				else:
                        		caseInfoLine = tempcaseFile.readline()
		else:
			return "N/A"
		return "N/A"
		
