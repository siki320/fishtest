# -*- coding: GB18030 -*-
# '''
# '''

class BaseDecoder(object):
	@classmethod
	def decode(self,data):
		pass

class BaseBodyDecoder(BaseDecoder):
    @classmethod
    def decode(self,data):
        pass

class BaseHeadDecoder(BaseDecoder):
    @classmethod
    def decode(self,data):
        pass

    @classmethod
    def getHeadSize(self):
        pass

    @classmethod
    def getBodySize(self,rawHead):
        pass

class BaseHeadBodyDecoder(BaseDecoder):
    @classmethod
    def decode(self,data):
        headSize = self.headDecoder.getHeadSize()
        head = self.headDecoder.decode(data[:headSize])
        if len(data) == headSize:
            body = {}
        else:
            body = self.bodyDecoder.decode(data[headSize:])
        return head, body

class BaseEncoder(object):
    @classmethod
    def encode(self,head,body):
        pass

class BaseBodyEncoder(BaseEncoder):
    @classmethod
    def encode(self,body):
        pass

class BaseHeadEncoder(BaseEncoder):
    @classmethod
    def encode(self,head,bodyLen):
        pass


    def getDefaultHead(self):
        pass

class BaseHeadBodyEncoder(BaseEncoder):
    @classmethod
    def encode(self,head,body):
        if body == {}:
            bodyLen = 0
            rawHead = self.headEncoder.encode(head,bodyLen)
            return rawHead

        rawBody, bodyLen = self.bodyEncoder.encode(body)
        rawHead = self.headEncoder.encode(head,bodyLen)
        return rawHead + rawBody
