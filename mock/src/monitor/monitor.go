package monitor

/*
   worker的实现罗辑
*/
import (
	"encoding/json"
	"sync"

	logger "helper/xlog4go"
)

type SendInfoData struct {
	Event string
	Value int64
	Type  string
}

var TotalDataPool *sync.Pool
var infochan = make(chan *SendInfoData, 1000000)
var inforespchan = make(chan string, 1000)
var InfoImpl *InfoResult

//info interface async process worker
func InfoWorker() {
	for {
		select {
		case data := <-infochan:
			dealinfodata(data)
		}
	}
}

func dealinfodata(data *SendInfoData) {
	datatype := data.Type
	event := data.Event
	switch datatype {
	case "AddReqCount":
		index, ok := InfoImpl.count_index[event]
		if ok {
			InfoImpl.Count[index].ReqCount += 1
		}
	case "AddRedisCount":
		index, ok := InfoImpl.count_index[event]
		if ok {
			InfoImpl.Count[index].RedisCount += 1
		}
	case "AddRepeatedError":
		index, ok := InfoImpl.error_index[event]
		if ok {
			InfoImpl.Error[index].RepeatedErr += 1
		}
	case "AddReqError":
		index, ok := InfoImpl.error_index[event]
		if ok {
			InfoImpl.Error[index].ReqErr += 1
		}

	case "AddFormatError":
		index, ok := InfoImpl.error_index[event]
		if ok {
			InfoImpl.Error[index].FormatErr += 1
		}
	case "AddRedisError":
		index, ok := InfoImpl.error_index[event]
		if ok {
			InfoImpl.Error[index].RedisErr += 1
		}
	case "AddProcessCostTime":
		index, ok := InfoImpl.timeused_index[event]
		if ok {
			InfoImpl.TimeUsed[index].processcostsum += data.Value
			InfoImpl.TimeUsed[index].processcount += 1
			if InfoImpl.TimeUsed[index].processcount != 0 {
				InfoImpl.TimeUsed[index].ProcessCostAvg = InfoImpl.TimeUsed[index].processcostsum / InfoImpl.TimeUsed[index].processcount
			}
			if data.Value > InfoImpl.TimeUsed[index].ProcessCostMax {
				InfoImpl.TimeUsed[index].ProcessCostMax = data.Value
			}
		}
	case "AddFetchCostTime":
		index, ok := InfoImpl.timeused_index[event]
		if ok {
			InfoImpl.TimeUsed[index].fetchcostsum += data.Value
			InfoImpl.TimeUsed[index].fetchcount += 1
			if InfoImpl.TimeUsed[index].fetchcount != 0 {
				InfoImpl.TimeUsed[index].FetchCostAvg = InfoImpl.TimeUsed[index].fetchcostsum / InfoImpl.TimeUsed[index].fetchcount
			}
			if data.Value > InfoImpl.TimeUsed[index].FetchCostMax {
				InfoImpl.TimeUsed[index].FetchCostMax = data.Value
			}
		}

	case "AddRedisCostTime":
		index, ok := InfoImpl.timeused_index[event]
		if ok {
			InfoImpl.TimeUsed[index].rediscostsum += data.Value
			InfoImpl.TimeUsed[index].rediscount += 1
			if InfoImpl.TimeUsed[index].rediscount != 0 {
				InfoImpl.TimeUsed[index].RedisCostAvg = InfoImpl.TimeUsed[index].rediscostsum / InfoImpl.TimeUsed[index].rediscount
			}
			if data.Value > InfoImpl.TimeUsed[index].RedisCostMax {
				InfoImpl.TimeUsed[index].RedisCostMax = data.Value
			}
		}
	case "AddMsgLatency":
		index, ok := InfoImpl.timeused_index[event]
		if ok {
			InfoImpl.TimeUsed[index].latencysum += data.Value
			InfoImpl.TimeUsed[index].msgcount += 1
			if InfoImpl.TimeUsed[index].msgcount != 0 {
				InfoImpl.TimeUsed[index].LatencyAvg = InfoImpl.TimeUsed[index].latencysum / InfoImpl.TimeUsed[index].msgcount
			}
			if data.Value > InfoImpl.TimeUsed[index].LatencyMax {
				InfoImpl.TimeUsed[index].LatencyMax = data.Value
			}
		}
	case "handle_info":
		jsonv, _ := json.Marshal(*InfoImpl)
		logger.Info("json:%s", string(jsonv))
		InfoImpl = NewInfoResult()
		inforespchan <- string(jsonv)
	}
	TotalDataPool.Put(data)
}
