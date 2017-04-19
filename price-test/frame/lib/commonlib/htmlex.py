# -*- coding: GB18030 -*-
'''
rewrite from html.py
'''

from frame.lib.thirdlib.pyh import *    # 提供pyh和本模块的统一接口

# ------ html 转义 ------
html_escape_table = {
                     "&" : "&amp;", 
                     '"' : "&quot;", 
                     ">" : "&gt;", 
                     "<" : "&lt;", 
                     " " : "&nbsp;", 
                     "\t" : "&nbsp;&nbsp;", 
                     "\n" : "<br/>"
                     }

def html_escape(text):
    '''@summary: inspired by http://wiki.python.org/moin/EscapingHtml'''
    return "".join(html_escape_table.get(c,c) for c in text)
# ------ (end) html 转义 ------


class dtstable(table):
    '''@summary: html table类，包装了默认的养眼样式'''
    def __init__(self):
        super(dtstable, self).__init__()
        
        self.line_cnt = 0    # 实现隔行阴影
        self.attributes["class"] = "dtstable"
        
    def add_head(self, *elems):
        '''@summary: 增加表格中表头
        @param elems:表头中的数据，每个元素都是字符串
        @note: <tr> <td> <p> <b> <span> text'''
        enc_elems = [html_escape(str(e)) for e in elems]
        self.add_head_raw(*enc_elems)
            
    def add_head_raw(self, *elems):
        '''@summary: 不对elem中的字符串转义，其他同add_head()
        @note: 可以用来输入含html元素的字符串'''
        tr_head = self << tr()
        tr_head.attributes["class"] = "dtstrhead"
    
        for elem in elems:
            elem = str(elem)
            
            td_head = tr_head << td()
            td_head.attributes["class"] = "dtstdhead"
            
            p_head = td_head << p()
            p_head.attributes["class"] = "dtsp"
            
            span_head = span(elem)
            span_head.attributes["class"] = "dtsspanhead"
            
            p_head << b(span_head)
            
    def add_body_line(self, *elems):
        '''@summary: 增加表格中一行
        @param elems: 一行中的数据，每个元素都是字符串
        @note: <tr> <td> <p> <b> <span> text
        @return: list of <td> added'''
        enc_elems = [html_escape(str(e)) for e in elems]
        return self.add_body_line_raw(*enc_elems)
            
    def add_body_line_raw(self, *elems):
        '''@summary: 不对elem中的字符串转义，其他同add_body_line()
        @note: 可以用来输入含html元素的字符串
        @return: list of <td> added'''
        # 背景色flag，偶数行着色
        if self.line_cnt % 2 == 0:
            bg_flag = False
        else:
            bg_flag = True
            
        self.line_cnt += 1  # 增加行数
        
        tr_body = self << tr()
        ret = []
        
        for elem in elems:
            elem = str(elem)
            
            td_body = tr_body << td()
            ret.append(td_body)
            if not bg_flag:
                td_body.attributes["class"] = "dtstdbodynobg"
            else:
                td_body.attributes["class"] = "dtstdbodybg"
            
            p_body = td_body << p()
            p_body.attributes["class"] = "dtsp"
            
            span_body = span(elem)
            span_body.attributes["class"] = "dtsspanbody"
            
            p_body << b(span_body)
            
        return ret
            
    # -------- 设置标签属性 --------
    @staticmethod
    def gen_css():
        '''@summary: 返回css字符串'''
        css_str = '''\
/* set table attr */
.dtstable{
    mso-style-name: MsoNormalTable;
    mso-tstyle-rowband-size: 0;
    mso-tstyle-colband-size: 0;
    mso-style-noshow: yes;
    mso-style-priority: 99;
    mso-style-qformat: yes;
    mso-para-margin: 0cm;
    mso-para-margin-bottom: .0001pt;
    mso-pagination: widow-orphan;
    font-size: 10.0pt;
    font-family: Times New Roman;
    border: 0;
    cellspacing: 0;
    cellpadding: 0;
    width: 100%;
    border-collapse: collapse;
    mso-yfti-tbllook: 1184;
    mso-padding-alt: 0cm 0cm 0cm 0cm;
}

/* set head line tr attr */
.dtstrhead{
    mso-yfti-irow: 0;
    mso-yfti-firstrow: yes;
}

/* set head line td attr */
.dtstdhead{
    border: solid #98BF21 1.0pt;
    background: #A7C942;
    padding: 4.5pt 4.5pt 4.5pt 9.0pt;
}

/* set p attr, p is used within all td */
.dtsp{
    mso-style-unhide: no;
    mso-style-qformat: yes;
    margin-bottom: .0001pt;
    mso-pagination: widow-orphan;
    font-size: 12.0pt;
    font-family: Times New Roman;
    mso-fareast-font-family: 宋体;
    line-height: 18px;
    margin: 0px;
    padding: 0px;
}

/* set head line span attr, span is used within p */
.dtsspanhead{
    lang: zh-CN;
    font-size: 9.0pt;
    font-family: Trebuchet MS,sans-serif;
    color: white;
    text-transform: uppercase;
    letter-spacing: 1.5pt;
}

/* set body line span attr, span is used within p */
.dtsspanbody{
    lang: zh-CN;
    font-size: 9.0pt;
    font-family: Trebuchet MS,sans-serif;
    color:black;
}

/* set body line td attr(odd line, no background) */
.dtstdbodynobg{
    border: solid #98BF21 1.0pt;
    background: white;
    padding: 3.0pt 2.25pt 3.0pt 9.0pt;
}

/* set body line td attr(even line, has background) */
.dtstdbodybg{
    border: solid #98BF21 1.0pt;
    background: #EAF2D3;
    padding: 3.0pt 2.25pt 3.0pt 9.0pt;
}'''

        return css_str
    # -------- (end) 设置标签属性 --------


class DtestPyh(PyH):
    def __init__(self, name="DtestPyHPage", encoding="utf-8"):
        super(DtestPyh, self).__init__(html_escape(name))
        
        # 设置语言为中文
        self.attributes["lang"] = "ZH-CN"
        
        # 设置编码格式
        self << meta(**{"http-equiv":"Content-Type", 
                        "content":"text/html; charset=%s"%encoding})


class dtestfont(font):
    def __init__(self, *arg, **kw):
        super(dtestfont, self).__init__(*arg, **kw)
        self.attributes["size"] = 3
        self.attributes["face"] = "arial"


def _test_dtstable():
    test_table = dtstable()
    test_table.add_head('case 名字', 'owner', 'details', 'time(ms)')
    for num in range(10):
        test_table.add_body_line('case/as/case1_error.py', 'caiyifeng', '<描述>\n\t这是第%s行描述' % (num+1), '0.119')
   
    #只获取table的html片段
    print test_table.render()

def _test_pyh():
    h = DtestPyh("DTS Test PYH")
    h.printOut()

if __name__ == '__main__':
    print "_test_dtstable:"
    _test_dtstable()
    
    print "\n_test_pyh:"
    _test_pyh()
    

