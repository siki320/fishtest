package httpserver

import (
	"net"
	"net/http"

	"global"
	logger "helper/xlog4go"
)

type HttpServerInstance struct {
	httpListener net.Listener
	httpServer   http.Server
	uri2Handler  map[string]*dInfoHttpHandler
}

var HttpInstance *HttpServerInstance

func NewHttpServerInstance() *HttpServerInstance {

	var hsi HttpServerInstance

	hsi.uri2Handler = make(map[string]*dInfoHttpHandler)

	//导出特征文件
	//hsi.uri2Handler["/canal/dump_feature"] = &dInfoHttpHandler{Name: "DumpFeature", Callfunc: HandleDumpFeature}
	//hsi.uri2Handler["/canal/get_count"] = &dInfoHttpHandler{Name: "GetCount", Callfunc: HandleGetCount}
	//hsi.uri2Handler["/canal/get_feature_count"] = &dInfoHttpHandler{Name: "GetFeatureCount", Callfunc: HandleGetFeatureCount}
	//hsi.uri2Handler["/canal/get_timeinfo"] = &dInfoHttpHandler{Name: "GetTimeInfo", Callfunc: HandleGetTimeInfo}
	//hsi.uri2Handler["/canal/info"] = &dInfoHttpHandler{Name: "Info", Callfunc: monitor.HandleInfo}
	hsi.uri2Handler["/gulfstream/api/v1/driver/dCheckDriver/index"] = &dInfoHttpHandler{Name: "dCheckDriver", Callfunc: HandledCheckDriver}
	hsi.uri2Handler["/bigdata-tagservice/integrate"] = &dInfoHttpHandler{Name: "CheckPassenger", Callfunc: HandleCheckPassenger}
	return &hsi

}

func (hsi *HttpServerInstance) Init() (err error) {

	mux := http.NewServeMux()
	for uri, handler := range hsi.uri2Handler {
		mux.Handle(uri, handler)
	}

	hsi.httpListener, err = net.Listen("tcp", ":"+global.Conf.Server.Port)
	if err != nil {
		return
	}
	defer hsi.httpListener.Close()

	hsi.httpServer = http.Server{Handler: mux}
	err = hsi.httpServer.Serve(hsi.httpListener)
	return
}

func (hsi *HttpServerInstance) Close() {
	logger.Info("close HttpServerInstance")
	hsi.httpListener.Close()

	for _, handler := range hsi.uri2Handler {
		handler.Close()
	}
	logger.Info("close HttpServerInstance 1 ")
}
