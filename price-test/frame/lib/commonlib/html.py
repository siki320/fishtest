# -*- coding: GB18030 -*-
'''
��ʹ��htmlex.py��ĳЩ�ӿڲ�һ�£����������ʹ��

@author: xuwei01 
@summary: ��OO��ʽ����html,�Լ���table�ķ�װ
@note: ��pyh�����ϵĸĽ���ԭ����ΪEmmanuel Turlay <turlay@cern.ch>
'''
__doc__ = """The pyh.py module is the core of the PyH package. PyH lets you
generate HTML tags from within your python code.
See http://code.google.com/p/pyh/ for documentation.
"""
__author__ = "Emmanuel Turlay <turlay@cern.ch>"
__version__ = '$Revision: 63 $'
__date__ = '$Date: 2010-05-21 03:09:03 +0200 (Fri, 21 May 2010) $'

import string
from sys import _getframe, stdout, modules, version
nOpen={}

nl = '\n'
doctype = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n'
charset = '<meta http-equiv="Content-Type" content="text/html;charset=utf-8" />\n'

tags = ['html', 'body', 'head', 'link', 'meta', 'div', 'p', 'form', 'legend', 
        'input', 'select', 'span', 'b', 'i', 'option', 'img', 'script',
        'table', 'tr', 'td', 'th', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'fieldset', 'a', 'title', 'body', 'head', 'title', 'script', 'br', 'table',
        'ul', 'li', 'ol', 'font']

selfClose = ['input', 'img', 'link', 'br']

class Tag(list):
    tagname = ''
    
    def __init__(self, *arg, **kw):
        self.attributes = kw
        if self.tagname : 
            name = self.tagname
            self.isSeq = False
        else: 
            name = 'sequence'
            self.isSeq = True
        self.id = kw.get('id', name)
        #self.extend(arg)
        for a in arg: self.addObj(a)

    def __iadd__(self, obj):
        if isinstance(obj, Tag) and obj.isSeq:
            for o in obj: self.addObj(o)
        else: self.addObj(obj)
        return self
    
    def addObj(self, obj):
        if not isinstance(obj, Tag): obj = str(obj)
        id=self.setID(obj)
        setattr(self, id, obj)
        self.append(obj)

    def setID(self, obj):
        if isinstance(obj, Tag):
            id = obj.id
            n = len([t for t in self if isinstance(t, Tag) and t.id.startswith(id)])
        else:
            id = 'content'
            n = len([t for t in self if not isinstance(t, Tag)])
        if n: id = '%s_%03i' % (id, n)
        if isinstance(obj, Tag): obj.id = id
        return id

    def __add__(self, obj):
        if self.tagname: return Tag(self, obj)
        self.addObj(obj)
        return self

    def __lshift__(self, obj):
        self += obj
        if isinstance(obj, Tag): return obj

    def render(self):
        result = ''
        if self.tagname:
            result = '<%s%s%s>' % (self.tagname, self.renderAtt(), self.selfClose()*' /')
        if not self.selfClose():
            for c in self:
                if isinstance(c, Tag):
                    result += c.render()
                else: result += c
            if self.tagname: 
                result += '</%s>' % self.tagname
        result += '\n'
        return result

    def renderAtt(self):
        result = ''
        for n, v in self.attributes.iteritems():
            if n != 'txt' and n != 'open':
                if n == 'cl': n = 'class'
                result += ' %s="%s"' % (n, v)
        return result

    def selfClose(self):
        return self.tagname in selfClose        
    
def TagFactory(name):
    class f(Tag):
        tagname = name
    f.__name__ = name
    return f

thisModule = modules[__name__]

for t in tags: setattr(thisModule, t, TagFactory(t)) 

def ValidW3C():
    out = a(img(src='http://www.w3.org/Icons/valid-xhtml10', alt='Valid XHTML 1.0 Strict'), href='http://validator.w3.org/check?uri=referer')
    return out

class PyH(Tag):
    tagname = 'html'
    
    def __init__(self, name='MyPyHPage'):
        self += head()
        self += body()
        self.attributes = dict(xmlns='http://www.w3.org/1999/xhtml', lang='en')
        self.head += title(name)

    def __iadd__(self, obj):
        if isinstance(obj, head) or isinstance(obj, body): self.addObj(obj)
        elif isinstance(obj, meta) or isinstance(obj, link): self.head += obj
        else:
            self.body += obj
            id=self.setID(obj)
            setattr(self, id, obj)
        return self

    def addJS(self, *arg):
        for f in arg: self.head += script(type='text/javascript', src=f)

    def addCSS(self, *arg):
        for f in arg: self.head += link(rel='stylesheet', type='text/css', href=f)
    
    def printOut(self,file=''):
        if file: f = open(file, 'w')
        else: f = stdout
        f.write(doctype)
        f.write(self.render())
        f.flush()
        if file: f.close()
   


def set_table_attr(table=None):
    '''
    @summary:����table������
    '''
    table.attributes['mso-style-name'] = 'MsoNormalTable'
    table.attributes['mso-tstyle-rowband-size'] = 0
    table.attributes['mso-tstyle-colband-size'] = 0
    table.attributes['mso-style-noshow'] = 'yes'
    table.attributes['mso-style-priority'] = 99
    table.attributes['mso-style-qformat'] = 'yes'
    table.attributes['mso-style-parent'] = ''
    table.attributes['mso-padding-alt'] = '0cm 5.4pt 0cm 5.4pt'
    table.attributes['mso-para-margin'] = '0cm'
    table.attributes['mso-para-margin-bottom'] = '.0001pt'
    table.attributes['mso-pagination'] = 'widow-orphan'
    table.attributes['font-size'] = '10.0pt'
    table.attributes['font-family'] = 'Times New Roman'
    table.attributes['border'] = '0'
    table.attributes['cellspacing'] = '0'
    table.attributes['cellpadding'] = '0'
    table.attributes['width'] = '100%'
    table.attributes['style'] = 'width:100.0%;border-collapse:collapse;mso-yfti-tbllook:1184;mso-padding-alt:0cm 0cm 0cm 0cm'


def set_tr_head_attr(tr):
    '''
    @summary: ����tr������  
    '''
    tr.attributes['style'] = 'mso-yfti-irow:0;mso-yfti-firstrow:yes'


def set_td_head_attr(td=None):
    '''
    @summary: ����table�б�ͷ�е�td������
    '''     
    td.attributes['style'] = 'border:solid #98BF21 1.0pt;background:#A7C942;padding:4.5pt 4.5pt 4.5pt 9.0pt'

def set_td_body_no_bg_attr(td=None):
    '''
    @summary: ����table��body���ֵ�td������(�����У��ޱ���ɫ)
    '''
    td.attributes['style'] = 'border:solid #98BF21 1.0pt;border-top:none;background:white; padding:3.0pt 2.25pt 3.0pt 9.0pt'

def set_td_body_bg_attr(td=None):
    '''
    @summary: ����table��body���ֵ�td������(ż���У��б���ɫ)
    '''
    td.attributes['style'] = 'border:solid #98BF21 1.0pt;border-top:none;background:#EAF2D3; padding:3.0pt 2.25pt 3.0pt 9.0pt'

def set_p_attr(p=None):
    '''
    @summary: ����p������
    '''
    p.attributes['mso-style-unhide'] = 'no'
    p.attributes['mso-style-qformat'] = 'yes'
    p.attributes['mso-style-parent'] = ''
    p.attributes['margin'] = '0cm'
    p.attributes['margin-bottom'] = '.0001pt'
    p.attributes['mso-pagination'] = 'widow-orphan'
    p.attributes['font-size'] = '12.0pt'
    p.attributes['font-family'] = 'Times New Roman'
    p.attributes['mso-fareast-font-family'] = '����'
    p.attributes['style'] = 'line-height:18px;margin:0px;padding:0px;'

def set_span_head_attr(span=None):
    '''
    @summary: ����table��head��span������
    '''
    span.attributes['lang'] = 'EN-US'
    span.attributes['style'] = 'font-size:9.0pt;font-family:\'Trebuchet MS\',\'sans-serif\';color:white;text-transform:uppercase;letter-spacing:1.5pt'


def set_span_body_attr(span=None):
    '''
    @summary: ����table��body��span������
    '''
    span.attributes['lang'] = 'EN-US'
    span.attributes['style'] = 'font-size:9.0pt;font-family:\'Trebuchet MS\',\'sans-serif\';color:black'


def handle_newline_symbol(src):
    '''
    @summary: ��"\n"ת��Ϊ"<br/>", ʹ���з�����html����ʾ
    @param src: ��Ҫ��ת����string 
    '''
    return string.replace(src, '\n', '<br/>')

def handle_space_symbol(src):
    '''
    @summary: ��" "ת��Ϊ"&nbsp", ʹ�ո������html����ʾ
    @param src: ��Ҫ��ת����string 
    '''
    return string.replace(src, ' ', '&nbsp')  

def handle_tab_symbol(src):
    '''
    @summary: ��"\t"ת��Ϊ"&nbsp&nbsp", ʹ1��tabת��Ϊ4���ո�����html����ʾ
    @param src: ��Ҫ��ת����string 
    '''
    return string.replace(src, '\t', '&nbsp&nbsp&nbsp&nbsp')   

def format_for_html(src):
    '''
    @summary: html����ʾ
    @param src: ��Ҫ��ת����string 
    '''
    return handle_newline_symbol(handle_space_symbol(handle_tab_symbol(src)))

def add_table_head(table_dest=None, *elems):
    '''
    @summary: ����table�ı�ͷ����
    @param table_dest: Ҫ��ӵ�table��pyh.table���ͣ� 
    @param elems: ��ͷ�еĸ�����Ŀ��string���ͣ�
    '''
    tr_head = table_dest << tr()
    set_tr_head_attr(tr_head)
    
    for elem in elems:
        td_head = tr_head << td()
        set_td_head_attr(td_head)
        p_head = td_head << p()
        set_p_attr(p_head)
        span_head = span(elem)
        set_span_head_attr(span_head)
        p_head << b(span_head)


def add_table_body_line(table_dest, bg_flag, *elems):
    '''
    @summary: ����table��body���֣�һ�У�
    @param table_dest: Ҫ��ӵ�table��pyh.table���ͣ� 
    @param elems: һ�еĸ�����Ŀ��string���ͣ�
    @param bg_flag: ��ʾ��һ���Ƿ���Ҫ����ɫ��bool���ͣ� 
    '''
    tr_body = table_dest << tr()
    
    for elem in elems:
        td_body = tr_body << td()
        if False == bg_flag:
            set_td_body_no_bg_attr(td_body)
        else:
            set_td_body_bg_attr(td_body)
        
        p_body = td_body << p()
        set_p_attr(p_body)
        span_body = span(elem)
        set_span_body_attr(span_body)
        p_body << b(span_body)

class DtestHtmlTable(table):
    '''
    @summary:DTS��html������
    @note:�û�ֻ��Ҫ���������ݡ����ɣ����ùܸ�ʽ�ϵ����
    '''
    def __init__(self):
        #self.tagname = "table"
        super(DtestHtmlTable, self).__init__()
        #Ϊ��ʵ�ָ�����Ӱ
        self.line_num = 0
        #����table�ĸ�ʽ
        set_table_attr(self)
        
    def add_head(self, *elems):
        '''
        @summary: ���ӱ���б�ͷ
        @param elems:��ͷ�е�����
        '''
        add_table_head(self, *elems)
        #����body�е�line_numΪ0��Ϊ������
        self.line_num = 0
        
    def add_body_line(self, *elems):
        '''
        @summary: ���ӱ����һ��
        @param elems: һ���е�����
        '''
        bg_flag = False        
        if 1 == self.line_num % 2:
            bg_flag = True
        self.line_num += 1
        
        add_table_body_line(self, bg_flag, *elems)
        
    def __str__(self):
        '''
        @summary: ����table��htmlƬ��(�ַ���)
        '''
        return self.render()
        

def _test():
    test_table = DtestHtmlTable()
    test_table.add_head('case name', 'owner', 'details', 'time(ms)')
    for num in range(10):
        test_table.add_body_line('case/as/case1_error.py', 'xuwei01', 'test1', '0.119')
   
    #ֻ��ȡtable��htmlƬ��
    print str(test_table)

if __name__ == '__main__':
    _test()
