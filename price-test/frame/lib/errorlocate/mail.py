# -*- coding: GB18030 -*-
'''
Created on May 22, 2012

@author: caiyifeng<caiyifeng>
'''

from frame.lib.commonlib import htmlex as html

class mail_html(object):
    def __init__(self):
        self.link_dict = {}
        self.__link_num = 0
        
    def _get_link_num(self):
        self.__link_num += 1
        return str(self.__link_num)
        
    def gen_mail_report(self, rulematch, mailpath):
        '''@param rulematch: 完成结果定位的rulematch对象
        @param mailpath: mail文件地址
        @attention: 为了配合hudson, 所有中文都被转码为utf-8'''
        # PyH对象
        mail_page = html.DtestPyh("dts_error_locate_report")
        mail_page.head << html.style(html.dtstable.gen_css(), type="text/css")
        
        # ----- 定位结果 -----
        mail_page << html.a(name="TOP")
        mail_page << html.p() << html.b() << html.dtestfont("Error Locate Result")
        
        result_table = mail_page << html.dtstable()
        result_table.add_head("Person Responsible", "Module", "Failed Reason", "Failed Cases", "Link")
        
        self._dict_gen_table(result_table, rulematch.result_dict, ())
        # ----- (end)定位结果 -----
        
        # ----- 错误信息 -----
        mail_page << html.br() + html.br()
        mail_page << html.p() << html.b() << html.dtestfont("Detail Fail Information")
        
        self._gen_info_table(mail_page, rulematch.keyinfo_list)
        # ----- (end)错误信息 -----
        
        # 输出 html到文件中
        mail_page << html.br() + html.br()
        mail_page.printOut(mailpath)
    
    def _dict_gen_table(self, table, adict, pretds):
        '''@summary: 将dict转换为table
        @param table: pyh table object
        @param adict: 待转换的dict object
        @param pretds: 前导td tuple，用于保存首行对象，每个元素是(text, rowspan)'''
        for i, (sub_key, sub_val) in enumerate(adict.items()):
            if isinstance(sub_val, dict):
                rowspan = self._get_row_num(sub_val)    # sub_key的rowspan
                
                if i == 0:
                    self._dict_gen_table(table, sub_val, pretds+((sub_key, rowspan),) )
                else:
                    self._dict_gen_table(table, sub_val, ((sub_key, rowspan),) )     # 第二行，无需前导tds
            
            elif isinstance(sub_val, list):
                rowspan = len(sub_val)
                
                if i == 0:
                    self._list_gen_table(table, sub_val, pretds+((sub_key, rowspan),) )
                else:
                    self._list_gen_table(table, sub_val, ((sub_key, rowspan),) )     # 第二行，无需前导tds

    def _list_gen_table(self, table, alist, pretds):
        '''@summary: 将list转换为table
        @param table: pyh table object
        @param alist: 待转换的list object
        @param pretds: 前导td tuple，用于保存首行对象，每个元素是(text, rowspan)'''
        for i, cname in enumerate(alist):
            if cname not in self.link_dict:
                self.link_dict[cname] = self._get_link_num()     #case名作为超链接太长, 采用字典进行编号存储
            
            if i == 0:
                tdtedts = [html.html_escape(td[0]) for td in pretds]
                tdrowspans = [td[1] for td in pretds]
                
                param = tdtedts + [html.html_escape(cname), '<a href="#%s">click</a>'%self.link_dict[cname]]
                tds = table.add_body_line_raw(*param)
                
                # 对于所有前导tds，设置rowspan
                for i, rowspan in enumerate(tdrowspans):
                    tds[i].attributes["rowspan"] = rowspan
            else:
                table.add_body_line_raw(html.html_escape(cname), '<a href="#%s">click</a>'%self.link_dict[cname])
                    
    def _get_row_num(self, _dict):
        # 计算当前dict中的case个数
        num = 0
        for d in _dict.values():
            if isinstance(d, list):
                num += len(d)
            elif isinstance(d, dict):
                num += self._get_row_num(d)
        return num
    
    def _gen_info_table(self, page, keyinfo_list):
        for info in keyinfo_list:
            page << html.br()
            
            # 返回页首
            page << html.a("to top", href="#TOP")
            
            # 设置casename锚点
            for casename in info.get_casename_list():
                page << html.a(name=self.link_dict[casename])
            
            # 输出keyinfo信息
            info_table = page << html.dtstable()
            info_table.add_head("Items", "Information")
            info_table.add_body_line("Case List", "\n".join(info.get_casename_list()))
            
            # 以order为序输出
            info_dict = info.getInfo()
            for item in info_dict["order"]:
                if not item in info_dict:
                    continue
                
                val = info_dict[item]
                if isinstance(val, list):
                    val = "\n".join(val)
                
                info_table.add_body_line(item, val.decode("gb18030").encode("utf8"))
            
        
