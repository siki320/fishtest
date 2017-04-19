#!/usr/bin/python
#/***************************************************************************
# *
# *
# **************************************************************************/
#/**
# * @author yangming03
# * @date 2012/11/26
# * @version $Revision: 1.0
# *
# **/

class DtestEnum:
	def __init__(self):
		self.members = []
	def isMember(self, arg):
		for m in self.members:
			if m == arg:
				return True
		return False
	def getMembers(self):
		return self.members
if __name__ == '__main__':
	pass
