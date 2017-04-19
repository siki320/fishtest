# -*- coding: gb2312 -*- 

import re;
from frame.lib.commonlib.apicom.debug import *
from frame.lib.commonlib.apicom.macro import *
from frame.lib.commonlib.apicom.util import *
from frame.lib.commonlib.apicom.exception import *



#UI2US, US2AC common part
def getTime(h):
    t = str(h.time);
    return getStrTime(t);

def setTime(h,time):
    h.time = getIntTime(time);
    return 0;

def getQuery(h):
    return str(h.word);

def setQuery(h,query):
    if(getTestMode() != 'EXCEPTION'):
        if(len(query) >= MAX_QUERYWORD_LEN):
            raise ProtocolException('length:%d of query is out of boundary:%d.' %(len(query),MAX_QUERYWORD_LEN));

    h.word = query;
    return 0;

def getLanguage(h):
    return int(str(h.language));

def setLanguage(h,language ):
    #if(getTestMode() != 'EXCEPTION'):
    #    if(int(language) < 0 or int(language) > 3):
    #        raise ProtocolException('language:%s is out of boundary:%d.' %(language,3));

    h.language = language ;
    return 0;

def getIp(h):
    return str2ip(str(h.ip));

def setIp(h,ip ):
    h.ip = ip2str(ip);
    return 0;

def getInterPage(h):
    if(str(h.isInterPage) == '1'):
        return True;
    else:
        return False;

def setInterPage(h,isInterPage ):
    if(isInterPage == True):
        h.isInterPage = 1;
    else:
        h.isInterPage = 0;
    return 0;

def getBwsRetry(h):
    if(str(h.isBwsRetry) == '0'):
        return True;
    else:
        return False;

def setBwsRetry(h,isBwsRetry ):
    if(isBwsRetry == True):
        h.isBwsRetry = 0;
    else:
        h.isBwsRetry = 1;
    return 0;

def getDebug(h):
    if(str(h.isDebug) == '1'):
        return True;
    else:
        return False;

def setDebug(h,isDebug ):
    if(isDebug == True):
        h.isDebug = 1;
    else:
        h.isDebug = 0;
    return 0;

def getContentCluster(h):
    if(str(h.isContCluster) == '1'):
        return True;
    else:
        return False;

def setContentCluster(h,isContCluster ):
    if(isContCluster == True):
        h.isContCluster = 1;
    else:
        h.isContCluster = 0;
    return 0;

def getSiteCluster(h):
    if(str(h.isSiteCluster) == '1'):
        return True;
    else:
        return False;

def setSiteCluster(h,isSiteCluster ):
    if(isSiteCluster == True):
        h.isSiteCluster = 1;
    else:
        h.isSiteCluster = 0;
    return 0;

def getCodeType(h):
    return int(str(h.codeType));

def setCodeType(h,codeType ):
    h.codeType = codeType ;
    return 0;   

def getAccountName(h):
    return str(h.accountName);

def setAccountName(h,accountName ):
    if(getTestMode() != 'EXCEPTION'):
        if(len(accountName) >= ACCOUNT_NAME_LEN):
            raise ProtocolException('length:%d of accountName is out of boundary:%d.' %(len(accountName),ACCOUNT_NAME_LEN));

    h.accountName = accountName ;
    return 0;  

def getTemplateName(h):
    return str(h.templateName);

def setTemplateName(h,templateName ):
    if(getTestMode() != 'EXCEPTION'):
        if(len(templateName) >= TEMPLATE_NAME_LEN):
            raise ProtocolException('length:%d of templateName is out of boundary:%d.' %(len(templateName),TEMPLATE_NAME_LEN));

    h.templateName = templateName ;
    return 0;  

def getStrategyName(h):
    return str(h.strategyName);

def setStrategyName(h,strategyName ):
    if(getTestMode() != 'EXCEPTION'):
        if(len(strategyName) >= STRATEGY_NAME_LEN):
            raise ProtocolException('length:%d of strategyName is out of boundary:%d.' %(len(strategyName),STRATEGY_NAME_LEN));

    h.strategyName = strategyName ;
    return 0;  

def getSiteName(h):
    return str(h.siteName);

def setSiteName(h,siteName ):
    if(getTestMode() != 'EXCEPTION'):
        if(len(siteName) >= SITE_NAME_LEN):
            raise ProtocolException('length:%d of siteName is out of boundary:%d.' %(len(siteName),SITE_NAME_LEN));

    h.siteName = siteName ;
    return 0;  

def getLastModified(h):
    return str(h.lastModified);

def setLastModified(h,lastModified ):
    h.lastModified = lastModified ;
    return 0;  

def getQueryId(h):
    return int(str(h.queryId));

def setQueryId(h,queryId):
    h.queryId = queryId ;
    return 0;  


def getBeforeUrl(self,h):
    buf = self.export_bin(repr(h.beforeUrl));
    return buf.rstrip('\0');

def setBeforeUrl(h,beforeUrl ):
    if(getTestMode() != 'EXCEPTION'):
        if(len(beforeUrl) >= BEFORE_URL_LEN):
            raise ProtocolException('length:%d of beforeUrl is out of boundary:%d.' %(len(beforeUrl),BEFORE_URL_LEN));

    h.beforeUrl = beforeUrl;
    return 0;  


def getPageNum(h):
    return int(str(h.pageNum));

def setPageNum(h,pageNum ):
    """if(getTestMode() != 'EXCEPTION'):
        if(int(pageNum) < 0 or int(pageNum) > 760):
            raise ProtocolException('pageNum:%s is out of boundary:%d.' %(pageNum,760));"""
#   if (int(pageNum) > )
    h.pageNum = pageNum ;
    return 0;  

def getResNum(h):
    return int(str(h.resNum));

#ui2us,us2ac
def setResNum(h,resNum ):
    if(getTestMode() != 'EXCEPTION'):
        if(int(resNum) < 0 or int(resNum) > MAX_RESULT_ITEM):
            raise ProtocolException('resNum:%s is out of boundary:%d.' %(resNum,MAX_RESULT_ITEM));

    h.resNum = resNum ;
    return 0;  

def getUrlParam(h):
    return str(h.urlParam);

def setUrlParam(h,urlParam ):
    if(getTestMode() != 'EXCEPTION'):
        if(len(urlParam) >= URL_LEN):
            raise ProtocolException('length:%d of urlParam is out of boundary:%d.' %(len(urlParam),URL_LEN));

    h.urlParam = urlParam ;
    return 0;  

    
#AC2US,US2UI common part
def getQuerySex(h):
    if(int(str(h.queryInfo)) & QUERY_SEX_MASK ):
        return True;
    else:
        return False;

def setQuerySex(h,flag):
    if(flag == True):
        h.queryInfo = int(str(h.queryInfo)) | QUERY_SEX_MASK;
    else:
        h.queryInfo = int(str(h.queryInfo)) & ~QUERY_SEX_MASK;
    return 0;

def getQueryPolicy(h):
    if(int(str(h.queryInfo)) & QUERY_POLICY_MASK ):
        return True;
    else:
        return False;

def setQueryPolicy(h,flag):
    if(flag == True):
        h.queryInfo = int(str(h.queryInfo)) | QUERY_POLICY_MASK;
    else:
        h.queryInfo = int(str(h.queryInfo)) & ~QUERY_POLICY_MASK;
    return 0;

def getParsed(self,h):
    buf = self.export_bin(repr(h.parsed));
    return buf.rstrip('\0');
        

def setParsed(h,parsed):
    if(getTestMode() != 'EXCEPTION'):
        if(len(parsed) >= MAX_QUERYWORD_LEN):
            raise ProtocolException('length:%d of parsed is out of boundary:%d.' %(len(parsed),MAX_QUERYWORD_LEN));

    h.parsed = parsed;
    return 0;

def getHilight(self,h):
    buf = self.export_bin(repr(h.hilight));
    return buf.rstrip('\0');


def setHilight(h,hilight):
    if(getTestMode() != 'EXCEPTION'):
        if(len(hilight) >= MAX_QUERYWORD_LEN):
            raise ProtocolException('length:%d of hilight is out of boundary:%d.' %(len(hilight),MAX_QUERYWORD_LEN));

    h.hilight = hilight;
    return 0;
    
def getJcWord(h):
    return str(h.jcWord);

def setJcWord(h,jcWord):
    if(getTestMode() != 'EXCEPTION'):
        if(len(jcWord) >= MAX_QUERYWORD_LEN):
            raise ProtocolException('length:%d of jcWord is out of boundary:%d.' %(len(jcWord),MAX_QUERYWORD_LEN));
    h.jcWord = jcWord;
    return 0;

    
#common item part
def getItemWeight(h,index):
    if(getTestMode() != 'EXCEPTION'):
        resultNum = int(str(h.status));
        if(index >= resultNum):
            raise ProtocolException('index:%d is out of boundary:%d.',index,resultNum);

    w = int(str(h.items[index].bsRes.weight));
    w = w & WEIGHT_MASK;
    return w;

#high 16 bit is bs flag, low 16 bit is weight
def setItemWeight(h,index,weight):
    if(getTestMode() != 'EXCEPTION'):
        resultNum = int(str(h.status));
        if(index >= resultNum):
            raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));
    
        if(weight > MAX_WEIGHT):
            raise ProtocolException('weight:%d is out of boundary:%d.' %(weight,MAX_WEIGHT));

    oldW = int(str(h.items[index].bsRes.weight));
    w = (oldW & (~WEIGHT_MASK)) | weight;
    h.items[index].bsRes.weight = w;
    return 0;

#self: 协议对象
#h:能够访问协议结构体的句柄对象
#index:结果索引
def getItemTitle(self,h,index):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));
    
    return getSubDiInfo(self,h.items[index],AS_TITLE);

def setItemTitle(self,h,index,value):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));
    
    setSubDiInfo(self,h.items[index],AS_TITLE,value);
    return 0;


def getItemUrl(self,h,index):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));
    
    return getSubDiInfo(self,h.items[index],AS_URL);

def setItemUrl(self,h,index,value):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));
    
    setSubDiInfo(self,h.items[index],AS_URL,value);
    return 0;

def getItemAbstract(self,h,index):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));
    
    return getSubDiInfo(self,h.items[index],AS_ABSTRACT);

def setItemAbstract(self,h,index,value):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));
    
    setSubDiInfo(self,h.items[index],AS_ABSTRACT,value);
    return 0;

def getItemLastModify(self,h,index):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));
    
    return getSubDiInfo(self,h.items[index],AS_LM);
    
def setItemLastModify(self,h,index,value):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));
    
    setSubDiInfo(self,h.items[index],AS_LM,value);
    return 0;

def getItemSize(self,h,index):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));
    
    return getSubDiInfo(self,h.items[index],AS_SIZE);

def setItemSize(self,h,index,value):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));
    
    setSubDiInfo(self,h.items[index],AS_SIZE,value);
    return 0;

def getItemCodeType(self,h,index):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));
    
    return getSubDiInfo(self,h.items[index],AS_CODE);

def setItemCodeType(self,h,index,value):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));
    
    setSubDiInfo(self,h.items[index],AS_CODE,value);
    return 0;

def getItemDynAdjust(self,h,index):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));
    
    return getSubDiInfo(self,h.items[index],AS_DYNADJUST);

def setItemDynAdjust(self,h,index,value):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));
    
    setSubDiInfo(self,h.items[index],AS_DYNADJUST,value);
    return 0;

def getItemUrlno(h,index):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));
    
    return int(str(h.items[index].bsRes.urlno));

def setItemUrlno(h,index,urlno):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));
    
    h.items[index].bsRes.urlno = urlno;
    return 0;

def getItemBlockNo(h,index):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));
    
    return int(str(h.items[index].bsRes.bs_v));

def setItemBlockNo(h,index,bs_v):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));
    
    h.items[index].bsRes.bs_v = bs_v;
    return 0;

def getItemSuburlSign(h,index):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));
    
    return int(str(h.items[index].bsRes.bs_v));

def setItemSuburlSign(h,index,bs_v):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));
    
    h.items[index].bsRes.bs_v = bs_v;
    return 0;

def getItemSiteSign(h,index):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));

    s1 = int(str(h.items[index].bsRes.site_sign1));
    s2 = int(str(h.items[index].bsRes.mix_sign.site_sign2));
    return (s1 <<32) + s2;

def setItemSiteSign(h,index,siteSign):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));


    b = siteSign % (1<<32);
    a = siteSign >>32;

    h.items[index].bsRes.site_sign1 = a;
    h.items[index].bsRes.mix_sign.site_sign2 = b;
    return 0;

def getItemSexLevel(h,index):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));
    
    return int(str(h.items[index].bsRes.mix_sign.sex));

def setItemSexLevel(h,index,sex):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));

    if(sex < 0 or sex > 15):
        raise ProtocolException('sex:%d is out of boundary:%d.' %(sex,15));
    
    h.items[index].bsRes.mix_sign.sex = sex;
    return 0;

def getItemPolicyLevel(h,index):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));
    
    return int(str(h.items[index].bsRes.mix_sign.pol));

def setItemPolicyLevel(h,index,policy):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));

    if(policy < 0 or policy > 15):
        raise ProtocolException('policy:%d is out of boundary:%d.' %(policy,15));
        
    h.items[index].bsRes.mix_sign.pol = policy;
    return 0;

def getItemContentSign(h,index):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));
    
    return int(str(h.items[index].bsRes.cont_sign));

def setItemContentSign(h,index,cont_sign):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));

    h.items[index].bsRes.cont_sign = cont_sign;
    return 0;    

def getItemMatchProp(h,index):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));
    
    return int(str(h.items[index].bsRes.match_prop));

def setItemMatchProp(h,index,match_prop):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));
    
    h.items[index].bsRes.match_prop = match_prop;
    return 0; 
    
def getTitleList(self,h):
    index = 0;
    num = int(str(self.num));
    resList = [];
    while(index < num):
        resList.append(getItemTitle(self,h,index));
        index += 1;
    return resList;

def getUrlList(self,h):
    index = 0;
    num = int(str(self.num));
    resList = [];
    while(index < num):
        resList.append(getItemUrl(self,h,index));
        index += 1;
    return resList;

def getWeightList(self,h):
    index = 0;
    num = int(str(self.num));
    resList = [];
    while(index < num):
        resList.append(getItemWeight(h,index));
        index += 1;
    return resList;


def getItemStrategy(h,index):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));
    
    return [int(str(h.items[index].bsRes.strategy)),
            int(str(h.strategyEx[index].s1)),
            int(str(h.strategyEx[index].s2)),
            int(str(h.strategyEx[index].s3))];

def setItemStrategy(h,index,s0,s1,s2,s3):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));
  
    h.items[index].bsRes.strategy = s0;
    h.strategyEx[index].s1 = s1;
    h.strategyEx[index].s2 = s2;
    h.strategyEx[index].s3 = s3;
    return 0;


def getItemTiebaResult(url):
    m1 = re.match('^(?i)http://',url.strip());
    if(m1):
        return True;
    else:
        return False;
        
def getItemIknowResult(url):
    m1 = re.match('^(?i)http://',url.strip());
    if(m1):
        return True;
    else:
        return False;


def getItemUrlResult(h,index):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));

    if(int(str(h.items[index].bsRes.strategy)) & RESULT_URL_MASK ):
        return True;
    else:
        return False;

def setItemUrlResult(h,index,flag):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));

    if(flag == True):
        h.items[index].bsRes.strategy = int(str(h.items[index].bsRes.strategy)) | RESULT_URL_MASK;
    else:
        h.items[index].bsRes.strategy = int(str(h.items[index].bsRes.strategy)) & ~RESULT_URL_MASK;
    return 0;

def getItemJiucuoResult(h,index):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));

    if(int(str(h.items[index].bsRes.strategy)) & RESULT_JIUCUO_MASK ):
        return True;
    else:
        return False;

def setItemJiucuoResult(h,index,flag):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));

    if(flag == True):
        h.items[index].bsRes.strategy = int(str(h.items[index].bsRes.strategy)) | RESULT_JIUCUO_MASK;
    else:
        h.items[index].bsRes.strategy = int(str(h.items[index].bsRes.strategy)) & ~RESULT_JIUCUO_MASK;
    return 0;

def getItemZhidaResult(h,index):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));

    if(int(str(h.items[index].bsRes.strategy)) & RESULT_ZHIDA_MASK ):
        return True;
    else:
        return False;

def setItemZhidaResult(h,index,flag):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));

    if(flag == True):
        h.items[index].bsRes.strategy = int(str(h.items[index].bsRes.strategy)) | RESULT_ZHIDA_MASK;
    else:
        h.items[index].bsRes.strategy = int(str(h.items[index].bsRes.strategy)) & ~RESULT_ZHIDA_MASK;
    return 0;    


def getItemSiteCluster(h,index):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));

    if(int(str(h.items[index].bsRes.strategy)) & RESULT_SITE_CLUSTER_MASK ):
        return True;
    else:
        return False;

def setItemSiteCluster(h,index,flag):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));

    if(flag == True):
        h.items[index].bsRes.strategy = int(str(h.items[index].bsRes.strategy)) | RESULT_SITE_CLUSTER_MASK;
    else:
        h.items[index].bsRes.strategy = int(str(h.items[index].bsRes.strategy)) & ~RESULT_SITE_CLUSTER_MASK;

    return 0;   


def getItemContentCluster(h,index):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));

    if(int(str(h.items[index].bsRes.strategy)) & RESULT_CONTENT_CLUSTER_MASK ):
        return True;
    else:
        return False;

def setItemContentCluster(h,index,flag):
    resultNum = int(str(h.status));
    if(index >= resultNum):
        raise ProtocolException('index:%d is out of boundary:%d.' %(index,resultNum));

    if(flag == True):
        h.items[index].bsRes.strategy = int(str(h.items[index].bsRes.strategy)) | RESULT_CONTENT_CLUSTER_MASK;
    else:
        h.items[index].bsRes.strategy = int(str(h.items[index].bsRes.strategy)) & ~RESULT_CONTENT_CLUSTER_MASK;

    return 0;       



#index:int, subinfo 内部索引
def getSubDiInfo(self,h,index):
    offset0 = int(str(h.offset[0]));
    if(getTestMode() != 'EXCEPTION'):
        if(offset0 != AS_DI_FILD_NUM - 1): 
            raise ProtocolException('offset[0]:%s is not equal to AS_DI_FILD_NUM-1:%s' %(offset0,AS_DI_FILD_NUM-1));
    key = repr(h.diInfo);
    diInfo = self.export_bin(key);
    if(index == AS_TITLE):
        beginPos = 0;
    else:
        beginPos = int(str(h.offset[index]));
        
    if(index == AS_ABSTRACT):
        endPos = None;
        buf = diInfo[beginPos:endPos];
        return buf.rstrip('\0');
    else:
        endPos = int(str(h.offset[index+1]));        

    return diInfo[beginPos:endPos].rstrip('\0');

def setSubDiInfo(self,h,index,value):
    key = repr(h.diInfo);
    value = value + '\0';
    
    diInfo = self.export_bin(key);

    offsetList = [];    
    offsetList.append(0);   
    for i in range(1,AS_DI_FILD_NUM):
        offsetList.append(int(str(h.offset[i])));    
  
    offsetList.append(MAX_DIINFO_SIZE);    
    
    diInfoList = [];
    for i in  range(0,AS_DI_FILD_NUM):       
        diInfoList.append(diInfo[offsetList[i]:offsetList[i+1]])
        
    if(getTestMode() != 'EXCEPTION'):    
        if(len(diInfoList) != AS_DI_FILD_NUM):
            raise ProtocolException("diInfoList:%d is not equal to AS_DI_FILD_NUM:%d" %(len(diInfoList),AS_DI_FILD_NUM));

    oldLen = len(diInfoList[index]);
    newLen = len(value);
    diInfoList[index] = value;
    diInfo = ''.join(diInfoList);

    for i in range(1,AS_DI_FILD_NUM):
        if (i > index):
            h.offset[i] = offsetList[i] + newLen - oldLen;

    h.diInfo = diInfo;
  
    return 0;    

def setSpNeed(h,index,srcid,degree,subclass,refresh):
    h.query_need.nodes[index].src_id = srcid;
    h.query_need.nodes[index].degree = degree;
    h.query_need.nodes[index].subclass = subclass;
    h.query_need.nodes[index].refresh = refresh;
    return 0;


def setLocalCode(h,nation,province,city,town):
    h.local_code.nation = nation;
    h.local_code.province = province;
    h.local_code.city = city;
    h.local_code.town = town;
    return 0;

def setLocalExtendCode(h,nation,province,city,town):
    h.local_code.nation = nation;
    h.local_code.province = province;
    h.local_code.city = city;
    h.local_code.town = town;
    return 0;

def setTimeRequest(h,type1,value):
    h.time_request.type = type1;
    h.time_request.ext_value = value;
    return 0;

def getHilightWordList(self,h):
    buf = getHilight(self,h);
    bl =  buf.split('\0');

    count = 0;
    for id,item in enumerate(bl):
        if (len(item) > 0):
            count += 1;
            bl[id] = item.strip('\1');
    bl = bl[:count];  # remove the last '' str
        
    return bl;
    
def setHilightWordList(h,arg):
    buf = "";

    for item in arg:
        buf += '\1' + item + '\1\0';

    setHilight(h,buf);
    return 0;



    
