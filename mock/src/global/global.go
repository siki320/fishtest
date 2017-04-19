package global

import (
	"helper/common"
	"sync/atomic"
)

const DCHECKDRIVER = "dCheckDriver"
const DCHECKPASSEN = "CheckPassenger"

var LogFile = "./conf/log.json"
var ConfFile = "./conf/api-mock.conf"
var Conf Config
var StopChan = make(chan bool, 1)
var StatQuitChan = make(chan int, 10)
var IsRunning = true

type LogId int64

func (i *LogId) GetNextId() int64 {
	return atomic.AddInt64((*int64)(i), 1)
}

var LogidGenerator LogId //logid 生产器

func init() {
	LogidGenerator = LogId(common.NowInNs())
}
