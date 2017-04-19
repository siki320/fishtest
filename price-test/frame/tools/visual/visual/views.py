import os
os.sys.path.append(os.path.dirname(os.path.abspath(__file__))+"/../../")
from django.template.loader import get_template
from django.template import Template, Context
from django.http import HttpResponse
import datetime
#from frame.lib.commonlib.logreader import LogReader

def index(request):
    #now = datetime.datetime.now()
    #html = "<html><body>Hello world, it is now %s.</body></html>" % now
    t = get_template('index.htm')
    #open conf files
    #here is a stub
    visualconf = {
        "module":[["UI",500,0], ["RS",500,180], ["UFS-STUB",200,180],  ["index",500,540]],
        "line"  :[[500,0,500,180],[200,180,500,180],[500,540,500,180]],
        "log"   :[
                  ["logfetch/home/zhaiyao/rserver/ers/log/ers.log#tail",800, 0, 360, 180],
                  ["logfetch/home/zhaiyao/rserver/TEST_ENV/rserver/log/rserver.log#tail",550,200, 360, 180],
                  ["logfetch/home/zhaiyao/rserver/TEST_ENV/rserver/log/rserver.log.wf#tail",100,200, 360, 90],
                  ["logfetch/home/zhaiyao/rserver/TEST_ENV/index/log/indexlog#tail", 550, 400, 360, 180],
                  ["logfetch/home/zhaiyao/rserver/TEST_ENV/index/log/indexlog.wf#tail", 100, 400, 360, 90],          
                 ],
    }
    html = t.render(Context({"modules":visualconf["module"],"lines":visualconf["line"],"logs":visualconf["log"]}))
    return HttpResponse(html)



def logfetch(request, logpath="default"):
    logpath = logpath
    loginfo = ""
    try:
        logfile = open(str(logpath))
        loginfo = logfile.read()
        logfile.close()
        loginfo = loginfo.split("\n")
        if len(loginfo) > 40:
            loginfo = loginfo[-40:]
        #log info is a list
    except:
        loginfo = ["Refreshing.","Please wait."]
    t = get_template('logfetch.htm')
    html = t.render(Context({'logpath':logpath,'loginfo':loginfo}))
    return HttpResponse(html)



