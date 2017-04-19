package httpserver

import (
	"encoding/json"
	"io"
	"net/http"
	"runtime/debug"
	"sync"

	"global"
	"helper/common"
	logger "helper/xlog4go"
)

type HttpResponse struct {
	ErrNo  int    `json:"errno"`
	ErrMsg string `json:"errmsg"`
	LogId  int64  `json:"logid"`
}

func doResponse(errno int, errmsg string, logid int64, writer io.Writer) {

	retInfo, err := json.Marshal(HttpResponse{
		ErrNo:  errno,
		ErrMsg: errmsg,
		LogId:  logid,
	})
	if err != nil {
		logger.Warn("")
		return
	}
	io.WriteString(writer, string(retInfo))

}

func HandleError(src string, funcname string) {
	if err := recover(); err != nil {
		errMsg := "src=" + src + " funcname=" + funcname + " is err."
		logger.Info("HttpHandleError# recover errno:%d errssg:%s stack:%s", global.ERRNO_PANIC, errMsg, string(debug.Stack()))
	}
}

type dInfoHttpHandler struct {
	Name     string
	wg       sync.WaitGroup
	Callfunc func(w http.ResponseWriter, r *http.Request, logId int64)
}

func (chh *dInfoHttpHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	chh.wg.Add(1)
	defer chh.wg.Done()

	logId := global.LogidGenerator.GetNextId()

	clientLogId := r.Header.Get("didi-header-rid")
	r.ParseForm()

	src := r.URL.Query().Get("src")

	defer HandleError(src, chh.Name)

	tBegin := common.NowInMs()

	chh.Callfunc(w, r, logId)

	logger.Info("[traceid %s src:%s logId %d]URL:%s Value:%v Host:%s RemotAddr:%s %s[%s]# all_cost: %d ms", clientLogId, src, logId, r.URL.Path, r.Form, r.Host, r.RemoteAddr, chh.Name, clientLogId, common.NowInMs()-tBegin)
}

func (chh *dInfoHttpHandler) Close() {
	chh.wg.Wait()
}
