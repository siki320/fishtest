package httpserver

import (
	"encoding/json"
	"io"
	"net/http"
	"strconv"
	"strings"
	"time"

	"global"
	logger "helper/xlog4go"
	"monitor"
)

type dCheckDriverRequest struct {
	didlist   []string
	timestamp string
}
type dCheckDriverResponse struct {
	Errno      int                    `json:"errno"`
	Data       map[string]interface{} `json:"data"`
	Is_busy    map[string]interface{} `json:"is_busy"`
	Product_id map[string]interface{} `json:"product_id"`
	Is_carpool map[string]interface{} `json:"is_carpool"`
}

func HandledCheckDriver(w http.ResponseWriter, r *http.Request, logid int64) {
	monitor.InfoImpl.AddReqCount(global.DCHECKDRIVER)
	begintime := time.Now()

	r.ParseForm()
	didlist := strings.TrimSpace(r.FormValue("didlist"))
	timestamp := strings.TrimSpace(r.FormValue("timestamp"))
	logger.Info("dCheckDriver, didlist:%+v,timestamp:%+v", didlist, timestamp)
	request := &dCheckDriverRequest{
		didlist:   make([]string, 0),
		timestamp: timestamp,
	}
	for _, driverId := range strings.Split(didlist, ",") {
		request.didlist = append(request.didlist, driverId)
	}

	response := &dCheckDriverResponse{
		Errno:      0,
		Data:       make(map[string]interface{}, 0),
		Is_busy:    make(map[string]interface{}, 0),
		Product_id: make(map[string]interface{}, 0),
		Is_carpool: make(map[string]interface{}, 0),
	}

	if err := dCheckDriver(request, response, logid); err != nil {
		response.Errno = global.ERROR_INTERNAL
	}
	jsonString, err := json.Marshal(response)
	if err != nil {
		logger.Error("HandledCheckDriver Marshal response failed,logid:%d,err:%s,response:%+v", logid, err.Error, response)
	}
	//logger.Info("HandledCheckDriver logid:%d, request:%+v,reponse:%+v", logid, request, response)

	io.WriteString(w, string(jsonString))
	duration := time.Since(begintime)
	monitor.InfoImpl.AddProcessCostTime(global.DCHECKDRIVER, int64(duration/time.Microsecond))
	return
}

func dCheckDriver(request *dCheckDriverRequest, response *dCheckDriverResponse, logid int64) error {
	for _, driverId := range request.didlist {
		did, _ := TransToInt(driverId)
		//did, _ := TransToInt64(driverId)
		if did%2 == 0 {
			response.Data[driverId] = 0 // canlisten
		} else {
			response.Data[driverId] = 1
		}
		response.Is_busy[driverId] = 1
		response.Product_id[driverId] = 3
		response.Is_carpool[driverId] = 2
	}
	logger.Info("dCheckDriver, logid:%d, request:%+v,response:%+v", logid, request, response)
	return nil
}

func TransToInt(data interface{}) (res int, err error) {
	switch data.(type) {
	case float64:
		res = int(data.(float64))
	case int:
	case string:
		res, err = strconv.Atoi(strings.TrimSpace(data.(string)))
	}
	return
}

func TransToInt64(data interface{}) (res int64, err error) {
	switch data.(type) {
	case float64:
		res = int64(data.(float64))
	case int:
		res = int64(data.(int))
	case uint:
		res = int64(data.(uint))
	case int64:
	case string:
		res, err = strconv.ParseInt(strings.TrimSpace(data.(string)), 10, 64)
	}
	return
}
