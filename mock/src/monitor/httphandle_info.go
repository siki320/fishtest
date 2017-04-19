package monitor

/*
   各个Http接口的逻辑实现
*/

import (
	"fmt"
	"io"
	"net/http"

	"helper/common"
	logger "helper/xlog4go"
)

var EventList = []string{
	"bubble",
	"ordercreated",
	"ordercreateddpid",
	"orderstrived",
	"orderfinished",
	"ordercanceled",
	"dumpfeature",
	"getfeaturecount",
	"taxi_bubble",
	"taxi_order",
	"taxi_order_create",
	"taxi_order_strive",
	"taxi_order_finish",
}

type CountNode struct {
	Event      string `json:"event"`
	ReqCount   int64  `json:"reqcount"`
	RedisCount int64  `json:"rediscount"`
}

type TimeUsedNode struct {
	Event          string `json:"event"`
	ProcessCostAvg int64  `json:"processcostavg"`
	processcount   int64
	processcostsum int64
	ProcessCostMax int64 `json:"processcostmax"`
	FetchCostAvg   int64 `json:"fetchcostavg"`
	fetchcount     int64
	fetchcostsum   int64
	FetchCostMax   int64 `json:"fetchcostmax"`
	RedisCostAvg   int64 `json:"rediscostavg"`
	rediscount     int64
	rediscostsum   int64
	RedisCostMax   int64 `json:"rediscostmax"`
	LatencyAvg     int64 `json:"latencyavg"`
	msgcount       int64
	latencysum     int64
	LatencyMax     int64 `json:"latencymax"`
}

type ResourceNode struct {
	Mem int64   `json:"mem"`
	Cpu float64 `json:"cpu"`
}

type ErrorNode struct {
	Event       string `json:"event"`
	RepeatedErr int64  `json:"repeatederr"`
	FormatErr   int64  `json:"formaterr"`
	RedisErr    int64  `json:"rediserr"`
	ReqErr      int64  `json:"reqerr"`
}

type InfoResult struct {
	Count          []CountNode    `json:"count"`
	TimeUsed       []TimeUsedNode `json:"timeused"`
	Resource       []ResourceNode `json:"resource"`
	Error          []ErrorNode    `json:"error"`
	count_index    map[string]int
	timeused_index map[string]int
	error_index    map[string]int
}

//create a new InfoResult struct
func NewInfoResult() *InfoResult {
	CountSlice := make([]CountNode, 0)
	TimeUsedSlice := make([]TimeUsedNode, 0)
	ErrorSlice := make([]ErrorNode, 0)
	ResourceSlice := make([]ResourceNode, 0)
	t_count_index := make(map[string]int)
	t_timeused_index := make(map[string]int)
	t_error_index := make(map[string]int)
	for i, event := range EventList {
		countnode := &CountNode{Event: event}
		t_count_index[event] = i
		CountSlice = append(CountSlice, *countnode)

		timeusednode := &TimeUsedNode{Event: event}
		t_timeused_index[event] = i
		TimeUsedSlice = append(TimeUsedSlice, *timeusednode)

		errornode := &ErrorNode{Event: event}
		t_error_index[event] = i
		ErrorSlice = append(ErrorSlice, *errornode)
	}
	resourceN := &ResourceNode{}
	ResourceSlice = append(ResourceSlice, *resourceN)
	res := &InfoResult{Count: CountSlice, TimeUsed: TimeUsedSlice, Resource: ResourceSlice, Error: ErrorSlice, count_index: t_count_index, timeused_index: t_timeused_index, error_index: t_error_index}
	return res
}

func (inforesult *InfoResult) AddReqCount(event string) {
	sd := TotalDataPool.Get().(*SendInfoData)
	sd.Event = event
	sd.Type = "AddReqCount"
	infochan <- sd
}

func (inforesult *InfoResult) AddRedisCount(event string) {
	sd := TotalDataPool.Get().(*SendInfoData)
	sd.Event = event
	sd.Type = "AddRedisCount"
	infochan <- sd
}

func (inforesult *InfoResult) AddRepeatedError(event string) {
	sd := TotalDataPool.Get().(*SendInfoData)
	sd.Event = event
	sd.Type = "AddRepeatedError"
	infochan <- sd
}

func (inforesult *InfoResult) AddFormatError(event string) {
	sd := TotalDataPool.Get().(*SendInfoData)
	sd.Event = event
	sd.Type = "AddFormatError"
	infochan <- sd
}

func (inforesult *InfoResult) AddReqError(event string) {
	sd := TotalDataPool.Get().(*SendInfoData)
	sd.Event = event
	sd.Type = "AddReqError"
	infochan <- sd
}

func (inforesult *InfoResult) AddRedisError(event string) {
	sd := TotalDataPool.Get().(*SendInfoData)
	sd.Event = event
	sd.Type = "AddRedisError"
	infochan <- sd
}

func (inforesult *InfoResult) AddProcessCostTime(event string, cost int64) {
	sd := TotalDataPool.Get().(*SendInfoData)
	sd.Event = event
	sd.Type = "AddProcessCostTime"
	sd.Value = cost
	infochan <- sd
}

func (inforesult *InfoResult) AddFetchCostTime(event string, cost int64) {
	sd := TotalDataPool.Get().(*SendInfoData)
	sd.Event = event
	sd.Type = "AddFetchCostTime"
	sd.Value = cost
	infochan <- sd
}

func (inforesult *InfoResult) AddRedisCostTime(event string, cost int64) {
	sd := TotalDataPool.Get().(*SendInfoData)
	sd.Event = event
	sd.Type = "AddRedisCostTime"
	sd.Value = cost
	infochan <- sd
}

func (inforesult *InfoResult) AddMsgLatency(event string, cost int64) {
	sd := TotalDataPool.Get().(*SendInfoData)
	sd.Event = event
	sd.Type = "AddMsgLatency"
	sd.Value = cost
	infochan <- sd
}

func HandleInfo(w http.ResponseWriter, r *http.Request, logid int64) {
	funcname := common.CallerName()
	logger.Info(fmt.Sprintf("%s[%d]", funcname, logid))

	//send cmd to info channel
	sd := TotalDataPool.Get().(*SendInfoData)
	sd.Type = "handle_info"
	infochan <- sd

	var jsonv string
	select {
	case jsonv = <-inforespchan:
	}
	io.WriteString(w, string(jsonv))
}
