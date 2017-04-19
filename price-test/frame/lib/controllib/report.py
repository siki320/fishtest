# -*- coding: GB18030 -*-
'''
'''

from xml.dom import minidom
import json

from frame.lib.commonlib.dlog import dlog
import frame.lib.commonlib.htmlex as html


class DtestReport(object):
    '''@summary: DResult�����࣬����result��չʾ'''
    def log_case_summary(self, result, resultpath):
        '''@summary: ��ӡcase summary��Ϣ
        @param result: DResult object
        @param resultpath: ���������ļ�·��'''
        # ���̧ͷ
        lines = []
        lines.append("Case Result:")
        lines.append("%s\t%s\t%s\t%s\t%s" % ("Case_Name", "Result", "Detail", "Failed_Tests", "Time(ms)"))

        # ���ָ��ֽ����case
        skip_case_lines = []
        pass_case_lines = []
        fail_case_lines = []

        for case_str in result.case_result_dict:
            if case_str in result.case_time_dict:
                atime = int(result.case_time_dict[case_str].totaltime * 1000)     # ����
            else:
                atime = 0

            r = result.case_result_dict[case_str]
            # print r

            if r.result == result.SKIP:
                skip_case_lines.append("%s\t%s\t%s" % (case_str, r, atime))
            elif r.result == result.PASS:
                pass_case_lines.append("%s\t%s\t%s" % (case_str, r, atime))
            elif r.result == result.FAILED:
                fail_case_lines.append("%s\t%s\t%s" % (case_str, r, atime))

        # ����������
        skip_case_lines.sort()
        pass_case_lines.sort()
        fail_case_lines.sort()

        # ���˳��skip, pass, fail
        lines.extend(skip_case_lines)
        lines.extend(pass_case_lines)
        lines.extend(fail_case_lines)

        # ������ܽ��
        ares_str = "P" if result.get_total_result() else "Failed"
        atime = int(result.alltime.totaltime * 1000)      # ����
        lines.append("%s\t%s\tFail/All=%s/%s\t\t%s(ms)"
                     % ("CaseSum", ares_str, len(fail_case_lines), result.get_casenum(), atime) )
        lines.append("%s\t\tFail/All=%s/%s\t\t"
                     % ("TestSum", result._get_failed_testnum(), result._get_testnum()) )
        lines.append("=" * 10 + "\tEnd__Case__Log\t" + "=" * 10)

        # �������־
        dlog.info("\n".join(lines))

        # ���������ļ�
        f = open(resultpath, "w")
        f.write("".join([l+"\n" for l in lines]) )
        f.close()

        # self.gen_json_data(result._get_failed_testnum(),len(skip_case_lines), "")
        result.gen_json_result(resultpath, result._get_testnum(), result._get_failed_testnum() )

        return lines

    def gen_json_data(self, case_fail,case_skip, resultpaath):
        json_result = "failed"
        json_failed_count = case_fail
        json_skipped_count = case_skip
        json_succeed_count = 0

        if case_fail == 0 :
            json_result = "succeed"

        result_obj = {
            "result":json_result,
            "categories": [
                {'cases': {'failed':{'count': json_failed_count }, 'skipped': {'count': json_skipped_count},'succeed': {'count': json_succeed_count}
                         }}]
        }
        print result_obj



    def log_times(self,result):
        '''
        @summary: ��־��¼ʱ����Ϣ
        '''
        total_case_time = sum([t.totaltime for t in result.case_time_dict.values()] )  # ��
        dlog.debug("Total Case Time : %s(s)", int(total_case_time))
        dlog.debug("Total Plugin Time. Benchmark : %d(s), Startup : %d(s)",
                     result.plugin_bench_timer.totaltime, result.plugin_startup_timer.totaltime)

    # ------ json���� -------
    def gen_json_result(self, result, jsonpath):
        '''@summary: ���json�����������ȫ����Ϣ����������Խ�����д���
        @param result: DResult object
        @param jsonpath: ���������ļ�·��'''
        f = open(jsonpath, "w")
        f.write(json.dumps(result, ensure_ascii=False, indent=2, default=self._serialize_dtestresult)+"\n")
        f.close()

    def gen_json_result_2(self,  jsonpath,sum_num,fail_num,skip_num):
        '''@summary: ���json�����������ȫ����Ϣ����������Խ�����д���
        @param result: DResult object
        @param jsonpath: ���������ļ�·��'''
        f = open(jsonpath, "w")

        result = "succeed"
        if fail_num == 0:
            result = "succeed"

        result_obj = {
            "total": {"count":sum_num},
             "succeed": {"count": sum_num-fail_num},
            "failed":{"count": fail_num},
            "skipped": {'count': 0},
            "error": {"count": 0}

                 }

        f.write(json.dumps(result_obj, ensure_ascii=False, indent=2, default=self._serialize_dtestresult)+"\n")
        f.close()

    def _serialize_dtestresult(self, result):
        '''@summary: ���л�DResult����'''
        return {
                "total_result": "P" if result.get_total_result() else "Failed",
                "case_num": result.get_casenum(),
                "failed_case_num": result.get_failed_casenum(),
                "test_num": result._get_testnum(),
                "failed_test_num": result._get_failed_testnum(),
                "all_time_ms": int(result.alltime.totaltime*1000),
                "extra_dict": result.depot,
                "plugin_bench_time_ms": int(result.plugin_bench_timer.totaltime*1000),
                "plugin_startup_time_ms": int(result.plugin_startup_timer.totaltime*1000),
                "start_time": result.start_time.strftime('%Y-%m-%d %H:%M:%S'),
                "end_time": result.end_time.strftime('%Y-%m-%d %H:%M:%S'),
                "case_result_dict": self._serialize_caseresult_dict(result.case_result_dict, result.case_time_dict, result)
                }

    def _serialize_caseresult_dict(self, rd, td, dtestresult):
        '''@param rd: CaseResult dict
        @param td: case time dict'''
        ret = {}
        for k,v in rd.items():
            t = td.get(k, None)
            ret[dtestresult._get_relpath(k)] = self._serialize_caseresult(v, t, dtestresult)
        return ret

    def _serialize_caseresult(self, result, timer, dtestresult):
        '''@summary: ���л�CaseResult����
        @param timer: Timer���󣬿���ΪNone'''
        if timer:
            time_ms = int(timer.totaltime * 1000)     # ����
        else:
            time_ms = 0

        return {
                "result": dtestresult.lit_dict[result.result],
                "detail": result.detail,
                "exc_stack": result.exc_stack,
                "time_ms": time_ms,
                "test_result_dict": self._serialize_testresult_dict(result.test_result_dict, dtestresult)
                }

    def _serialize_testresult_dict(self, rd, dtestresult):
        '''@param rd: TestResult dict'''
        ret = {}
        for k,v in rd.items():
            ret[k] = self._serialize_testresult(v, dtestresult)

        return ret

    def _serialize_testresult(self, result, dtestresult):
        '''@summary: ���л�TestResult����'''
        return {
                "result": dtestresult.lit_dict[result.result],
                "excstack": result.excstack
                }
    # ------ (end)json���� -------


    # ------ junit���� -------
    def gen_junit_report(self, result, junitpath, level):
        '''@summary: ����junit����
        @param result: DResult object
        @param junitpath: ���ɵ�junit·��
        @param level: ������"case" or "test"����ʾ��ͬ�ĵȼ�'''
        if level == "case":
            self._gen_junit_case_report(result, junitpath)

        elif level == "test":
            self._gen_junit_test_report(result, junitpath)

        else:
            raise Exception, "Unsupported level: %s" % level

    def _gen_junit_case_report(self, result, junitpath):
        '''@summary: ����case�����junit����
        @param result: DResult object'''
        imp = minidom.getDOMImplementation()
        doc = imp.createDocument(None, 'testsuites', None)
        root = doc.documentElement

        # schemaversion node
        version = doc.createElement("schemaversion")
        version.appendChild(doc.createTextNode("junit 1.0.0"))
        root.appendChild(version)

        # testsuite node
        testsuite = doc.createElement("testsuite")
        testsuite.setAttribute("name", "dts_cases")
        root.appendChild(testsuite)

        # case nodes
        for case_str in result.case_result_dict:
            casenode = doc.createElement("testcase")
            testsuite.appendChild(casenode)

            # set name
            casenode.setAttribute("name", result._get_relpath(case_str))
            testsuite.setAttribute("author", result._get_case_owner(case_str) )

            # set time
            if case_str in result.case_time_dict:
                atime = result.case_time_dict[case_str].totaltime
            else:
                atime = 0.0
            casenode.setAttribute("time", "%.3f" % atime)


            r = result.case_result_dict[case_str]

            # set failure
            if r.result == result.FAILED:
                fail = doc.createElement("failure")
                fail.setAttribute("message", r.detail)
                text = r.str_exc_stacks()
                fail.appendChild(doc.createTextNode("\n"+text))      # �����쳣ջ��Ϣ
                casenode.appendChild(fail)

            # set skipped
            if r.result == result.SKIP:
                skip = doc.createElement("skipped")
                casenode.appendChild(skip)

        # output
        f = open(junitpath, "w")
        doc.writexml(f, addindent="\t", newl="\n", encoding="GB18030")
        f.close()

    def _gen_junit_test_report(self, result, junitpath):
        '''@summary: ����test�����junit����
        @param result: DResult object'''
        imp = minidom.getDOMImplementation()
        doc = imp.createDocument(None, 'testsuites', None)
        root = doc.documentElement

        # schemaversion node
        version = doc.createElement("schemaversion")
        version.appendChild(doc.createTextNode("junit 1.0.0"))
        root.appendChild(version)

        summary = doc.createElement("summary")
        summary.setAttribute("name", "summary")
        summary.setAttribute("test_num", str(result._get_testnum()) )
        summary.setAttribute("test_fail_num", str(result._get_failed_testnum()) )
        root.appendChild(summary)

        # testsuite nodes
        for case_str in result.case_result_dict:
            testsuite = doc.createElement("testsuite")
            testsuite.setAttribute("name", result._get_relpath(case_str).replace(".py", "", 1) )      # ȥ��'.py'�����ⱻ��Ϊjava���������и�
            testsuite.setAttribute("author", result._get_case_owner(case_str) )
            testsuite.setAttribute("test_num", str(result.case_result_dict[case_str].get_testnum()) )
            testsuite.setAttribute("test_fail_num", str(result.case_result_dict[case_str].get_failed_testnum()) )
            root.appendChild(testsuite)


            if case_str in result.case_time_dict:
                atime = result.case_time_dict[case_str].totaltime
            else:
                atime = 0.0

            r = result.case_result_dict[case_str]

            # testcase nodes
            if r.get_testnum() == 0:
                # û������test���鹹һ��test
                anode = doc.createElement("testcase")
                anode.setAttribute("name", "result")
                anode.setAttribute("time", "%.3f" % atime)
                testsuite.appendChild(anode)

                # set failure
                if r.result == result.FAILED:
                    fail = doc.createElement("failure")
                    fail.setAttribute("message", r.detail)
                    text = r.exc_stack
                    fail.appendChild(doc.createTextNode(text))      # �����쳣ջ��Ϣ
                    anode.appendChild(fail)

                # set skipped
                if r.result == result.SKIP:
                    skip = doc.createElement("skipped")
                    anode.appendChild(skip)

            else:
                # ������test��ÿ��test��Ϊjunit�е�һ��testcase
                testtime = atime / r.get_testnum()      # ����testƽ��ʱ��

                for t in r.passed_tests + r.failed_tests:
                    anode = doc.createElement("testcase")
                    anode.setAttribute("name", t)
                    anode.setAttribute("time", "%.3f" % testtime)
                    testsuite.appendChild(anode)

                    if t in r.failed_tests:
                        # set failure
                        fail = doc.createElement("failure")
                        text = r.test_exc_stacks[r.failed_tests.index(t)]
                        fail.appendChild(doc.createTextNode(text))      # �����쳣ջ��Ϣ
                        anode.appendChild(fail)

        # output
        f = open(junitpath, "w")
        doc.writexml(f, addindent="\t", newl="\n", encoding="GB18030")
        f.close()
    # ------ (end)junit���� -------


    # ------ mail���� -------
    def gen_mail_report(self, result, mailpath, level, ejb):
        '''@summary: �����ʼ�����Ƭ��
        @attention: Ϊ�����hudson, �������Ķ���ת��Ϊutf-8
        @param result: DResult object
        @param mailpath: �����ʼ������·��
        @param level: "case"�� "test"����ʾ��ͬ�ĵȼ�
        @param ejb: ejbΪTrueʱ��������ȡdescription�е�EJB����'''

        if "case" == level:
            self._gen_mail_case_report(result, mailpath, ejb)
        elif "test" == level:
            self._gen_mail_test_report(result, mailpath, ejb)
        else:
            raise Exception, "Unsupported level: %s" % level

    def _gen_mail_case_report(self, result, mailpath, ejb):
        '''@summary: ����case�����ʼ�
        @attention: Ϊ�����hudson, �������Ķ���ת��Ϊutf-8
        @param result: DResult object'''
        # ���˳�FAILED��SKIP��case
        failed_case_list = []
        skipped_case_list = []
        pass_case_list = []

        for case_str in result.case_result_dict:
            r = result.case_result_dict[case_str]

            if result.FAILED == r.result:
                failed_case_list.append(case_str)
            elif result.SKIP == r.result:
                skipped_case_list.append(case_str)
            elif result.PASS == r.result:
                pass_case_list.append(case_str)

        failed_case_list.sort()
        skipped_case_list.sort()
        pass_case_list.sort()

        # PyH����
        mail_case_page = html.DtestPyh("dts_mail_case_report")
        mail_case_page.head << html.style(html.dtstable.gen_css(), type="text/css")

        # ----- ������Ϣ -------
        mail_case_page << html.p() << html.b() << html.dtestfont("Summary")

        # summary table
        summary_table = mail_case_page << html.dtstable()
        summary_table.add_head("", "Failed", "Pass", "Skip", "Total", "Time(s)")
        if failed_case_list:
            color="red"
        else:
            color="green"
        tds = summary_table.add_body_line_raw("Cases", '<span style="color:%s">%d</span>' % (color, len(failed_case_list)), len(pass_case_list),
                                              len(skipped_case_list), result.get_casenum(), "%.3f"%result.alltime.totaltime)
        tds[-1].attributes["rowspan"] = 2
        summary_table.add_body_line_raw("Tests", '<span style="color:%s">%d</span>' % (color, result._get_failed_testnum()),
                                        result._get_testnum()-result._get_failed_testnum(), "-", result._get_testnum())
        # ----- (end) ������Ϣ -------

        # ----- Fail case�� ------
        mail_case_page << html.br() + html.br()
        mail_case_page << html.p() << html.b() << html.dtestfont("Failed Cases")

        # failed case table
        failed_case_table = mail_case_page << html.dtstable()
        failed_case_table.add_head('case name', 'owner', 'details', 'time(s)', 'failed tests')

        for case_str in failed_case_list:
            case_name = result._get_relpath(case_str)
            case_owner = result._get_case_owner(case_str)
            if case_str in result.case_time_dict:
                case_time = result.case_time_dict[case_str].totaltime
            else:
                case_time = 0.0
            case_details = result.case_result_dict[case_str].detail

            failed_case_table.add_body_line(case_name, case_owner, case_details, "%.3f"%case_time,
                                            ",".join(result.case_result_dict[case_str].failed_tests))
        # ----- (end) Fail case�� ------

        # ----- Skip case�� ------
        mail_case_page << html.br() + html.br()
        mail_case_page << html.p() << html.b() << html.dtestfont("Skip Cases")

        # skip case table
        skip_case_table = mail_case_page << html.dtstable()
        skip_case_table.add_head('case name', 'owner', 'details')

        for case_str in skipped_case_list:
            case_name = result._get_relpath(case_str)
            case_owner = result._get_case_owner(case_str)
            case_details = result.case_result_dict[case_str].detail

            skip_case_table.add_body_line(case_name, case_owner, case_details)
        # ----- (end) Skip case�� ------

        # ----- fail ��ϸ��Ϣ�� -------
        mail_case_page << html.br() + html.br()
        mail_case_page << html.p() << html.b() << html.dtestfont("Failed Case information")

        # failed case table
        failed_info_table = mail_case_page << html.dtstable()
        failed_info_table.add_head('case name', 'stack', 'description','runtime log')

        for case_str in failed_case_list:
            case_name = result._get_relpath(case_str)
            case_stack = result.case_result_dict[case_str].str_exc_stacks().decode("gb18030",'replace').encode("utf-8")
            case_desc = result.case_result_dict[case_str].str_descs(ejb).decode("gb18030",'replace').encode("utf-8")
            case_runtime_log = result.case_result_dict[case_str].log_record.decode("gb18030",'replace').encode("utf-8")

            failed_info_table.add_body_line(case_name, case_stack, case_desc, case_runtime_log)
        # ----- (end) fail ��ϸ��Ϣ�� -------

        # ----- Pass case�� ------
        mail_case_page << html.br() + html.br()
        mail_case_page << html.p() << html.b() << html.dtestfont("Pass Cases")

        # pass case table
        pass_case_table = mail_case_page << html.dtstable()
        pass_case_table.add_head('case name', 'owner', 'time(s)')

        for case_str in pass_case_list:
            case_name = result._get_relpath(case_str)
            case_owner = result._get_case_owner(case_str)
            if case_str in result.case_time_dict:
                case_time = result.case_time_dict[case_str].totaltime
            else:
                case_time = 0.0

            pass_case_table.add_body_line(case_name, case_owner, "%.3f"%case_time)
        # ----- (end) Pass case�� ------

        # ��� html���ļ���
        mail_case_page << html.br() + html.br()
        mail_case_page.printOut(mailpath)

    def _gen_mail_test_report(self, result, mailpath, ejb):
        '''@summary: ����test�����ʼ�
        @attention: Ϊ�����hudson, �������Ķ���ת��Ϊutf-8
        @param result: DResult object'''
        # ���˳�FAILED��SKIP��case
        failed_case_list = []
        skipped_case_list = []
        pass_case_list = []

        for case_str in result.case_result_dict:
            r = result.case_result_dict[case_str]

            if result.FAILED == r.result:
                failed_case_list.append(case_str)
            elif result.SKIP == r.result:
                skipped_case_list.append(case_str)
            elif result.PASS == r.result:
                pass_case_list.append(case_str)

        failed_case_list.sort()
        skipped_case_list.sort()
        pass_case_list.sort()

        # PyH����
        mail_case_page = html.DtestPyh("dts_mail_test_report")
        mail_case_page.head << html.style(html.dtstable.gen_css(), type="text/css")

        # ----- ������Ϣ -------
        mail_case_page << html.p() << html.b() << html.dtestfont("Summary")

        # summary table
        summary_table = mail_case_page << html.dtstable()
        summary_table.add_head("", "Failed", "Pass", "Skip", "Total", "Time(s)")
        if failed_case_list:
            color="red"
        else:
            color="green"
        tds = summary_table.add_body_line_raw("Cases", '<span style="color:%s">%d</span>' % (color, len(failed_case_list)), len(pass_case_list),
                                              len(skipped_case_list), result.get_casenum(), "%.3f"%result.alltime.totaltime)
        tds[-1].attributes["rowspan"] = 2
        summary_table.add_body_line_raw("Tests", '<span style="color:%s">%d</span>' % (color, result._get_failed_testnum()),
                                        result._get_testnum()-result._get_failed_testnum(), "-", result._get_testnum())
        # ----- (end) ������Ϣ -------

        # ----- Fail test�� ------
        mail_case_page << html.br() + html.br()
        mail_case_page << html.p() << html.b() << html.dtestfont("Failed Tests")

        # failed case table
        failed_case_table = mail_case_page << html.dtstable()
        failed_case_table.add_head('case/test name', 'owner', 'details', 'time(s)')

        for case_str in failed_case_list:
            case_name = result._get_relpath(case_str)
            case_owner = result._get_case_owner(case_str)
            if case_str in result.case_time_dict:
                case_time = result.case_time_dict[case_str].totaltime
            else:
                case_time = 0.0
            case_details = result.case_result_dict[case_str].detail

            failed_case_table.add_body_line(case_name, case_owner, case_details, "%.3f"%case_time)


            for tname in result.case_result_dict[case_str].failed_tests:
                failed_case_table.add_body_line(" - "+tname, "", "", "")
        # ----- (end) Fail test�� ------

        # ----- Skip case�� ------
        mail_case_page << html.br() + html.br()
        mail_case_page << html.p() << html.b() << html.dtestfont("Skip Cases")

        # skip case table
        skip_case_table = mail_case_page << html.dtstable()
        skip_case_table.add_head('case name', 'owner', 'details')

        for case_str in skipped_case_list:
            case_name = result._get_relpath(case_str)
            case_owner = result._get_case_owner(case_str)
            case_details = result.case_result_dict[case_str].detail

            skip_case_table.add_body_line(case_name, case_owner, case_details)
        # ----- (end) Skip case�� ------

        # ----- fail ��ϸ��Ϣ�� -------
        mail_case_page << html.br() + html.br()
        mail_case_page << html.p() << html.b() << html.dtestfont("Failed Test information")

        # failed test table
        failed_info_table = mail_case_page << html.dtstable()
        failed_info_table.add_head('case/test name', 'stack', 'description')

        for case_str in failed_case_list:
            case_name = result._get_relpath(case_str)
            r = result.case_result_dict[case_str]

            failed_info_table.add_body_line(case_name,
                                            r.exc_stack.decode("gb18030",'replace').encode("utf-8"),
                                            r.get_desc(ejb).decode("gb18030",'replace').encode("utf-8"))

            for tname in r.failed_tests:
                tresult = r.test_result_dict[tname]
                failed_info_table.add_body_line(" - "+tname,
                                                tresult.excstack.decode("gb18030",'replace').encode("utf-8"),
                                                tresult.get_desc(ejb).decode("gb18030",'replace').encode("utf-8"))
        # ----- (end) fail ��ϸ��Ϣ�� -------

        # ----- Pass test�� ------
        mail_case_page << html.br() + html.br()
        mail_case_page << html.p() << html.b() << html.dtestfont("Pass Tests")

        # pass case table
        pass_case_table = mail_case_page << html.dtstable()
        pass_case_table.add_head('case/test name', 'owner', 'time(s)', 'description')

        # ����pass test��fail case
        some_fail_list = [case_str for case_str in failed_case_list if result.case_result_dict[case_str].get_passed_testnum()]

        for case_str in pass_case_list + some_fail_list:
            cr = result.case_result_dict[case_str]
            case_name = result._get_relpath(case_str)
            case_owner = result._get_case_owner(case_str)
            if case_str in result.case_time_dict:
                case_time = result.case_time_dict[case_str].totaltime
            else:
                case_time = 0.0

            if case_str in pass_case_list:
                pass_case_table.add_body_line(case_name, case_owner, "%.3f"%case_time, cr.get_desc(ejb).decode("gb18030",'replace').encode("utf-8"))
            else:
                pass_case_table.add_body_line(case_name+" (fail)", case_owner, "%.3f"%case_time, cr.get_desc(ejb).decode("gb18030",'replace').encode("utf-8"))


            for tname in result.case_result_dict[case_str].passed_tests:
                tr = cr.test_result_dict[tname]
                pass_case_table.add_body_line(" - "+tname, "", "", tr.get_desc(ejb).decode("gb18030",'replace').encode("utf-8"))
        # ----- (end) Pass test�� ------

        # ��� html���ļ���
        mail_case_page << html.br() + html.br()
        mail_case_page.printOut(mailpath)
    # ------ (end) mail���� -------

