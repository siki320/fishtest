# -*- coding: gb2312 -*- 


class APIException(Exception):
    def __init__(self, value):
        self.value = value;
    def __str__(self):
        return str(self.value);

class ProtocolException(APIException):
    def __init__(self, value):
        self.value = value;
    def __str__(self):
        return str(self.value);

class ServiceException(ProtocolException):
    def __init__(self, value):
        self.value = value;
    def __str__(self):
        return str(self.value);

class DictException(APIException):
    def __init__(self, value):
        self.value = value;
    def __str__(self):
        return str(self.value);
        
class AssertException(APIException):
    def __init__(self, value):
        self.value = value;
    def __str__(self):
        return str(self.value);        
        
class ExpectException(APIException):
    def __init__(self, value):
        self.value = value;
    def __str__(self):
        return str(self.value);   

class CaseException(APIException):
    def __init__(self, value):
        self.value = value;
    def __str__(self):
        return str(self.value);   

