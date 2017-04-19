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
from utils.dtsenum import DtestEnum
from logprint import Logger

class DtestContext(DtestEnum):
	TEST = "test"
	DEV = "dev"
	def __init__(self):
		self.members = [self.TEST, self.DEV]

class ContextManager:
	def __init__(self):
		self.context = {DtestContext.TEST : [] , DtestContext.DEV : []}
		self.itemList = []
		self.listList = []
		self.listSelectedPath = []
		self.cxtCategory =DtestContext()
		self.currentPlanList = []
		self.currentPlanIndex = None
		self.selectedIndex = None
		self.runList = []
		self.currentContextType = DtestContext.TEST

	def initialize(self):
		for cxtKey in self.context:
			self.context[cxtKey].append('DTS')

	def getPromptString(self):
		if self.cxtCategory.isMember(self.currentContextType):
			retVal = ""
			for pmpt in self.context[self.currentContextType]:
				retVal = "%s/%s"%(retVal, pmpt)
			return retVal[1:]

	def setPlanList(self, list):
		self.currentPlanList = list
	#need to change
	def getCurrentPlan(self):
		if self.currentPlanIndex == None:
			return None
		return self.currentPlanList[self.currentPlanIndex - 1][0]

	def getCurrentType(self):
		return self.currentPlanList[self.currentPlanIndex - 1][2]

	def getCurrentPlanFile(self):
		return self.currentPlanList[self.currentPlanIndex - 1][3]

	def selectItem(self, idx):
		if (0 == len(self.currentPlanList)):
			Logger.output("Empty Index")
			return False
		try:
			if self.isRoot():
				if self.selectedIndex == None:
					self.currentPlanIndex = idx
				else:
					self.currentPlanIndex = self.selectedIndex
			self.selectedIndex = idx

			if len(self.context[self.currentContextType]) < 2:
				if self.isRoot():
					self.context[self.currentContextType].append(self.getCurrentPlan())
			else:
				self.context[self.currentContextType].append(self.itemList[self.selectedIndex - 1])
		except IndexError:
			self.selectedIndex = None
			Logger.output("Select index out of range")
			return False
		return True

	def isRoot(self):
		return len(self.context[self.currentContextType])==1

	def getItemList(self):
		return self.itemList

	def push(self, list):
		if len(self.itemList) > 0:
			self.listList.append(self.itemList)
			if not self.isRoot():
				self.listSelectedPath.append(self.selectedIndex)
		self.itemList = list

	def pop(self, popLevel):
		if self.isRoot():
			return
		if len(self.listList) == 0:
			self.context[self.currentContextType].pop()
			self.currentPlugin = None
			self.selectedIndex = None
