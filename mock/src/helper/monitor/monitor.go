package monitor

import (
	"fmt"
	logger "github.com/shengkehua/xlog4go"
	"os"
	"time"
)

type Monitor struct {
	PrintFile     string
	PrintInterval int

	ReqCount  int64
	FailCount int64
}

var MonitorImpl *Monitor

func (monitor *Monitor) AddReqCount() {
	monitor.ReqCount += 1
}

func (monitor *Monitor) AddFailCount() {
	monitor.FailCount += 1
}

func (monitor *Monitor) Print() {
	userFile := monitor.PrintFile

	fout, err := os.OpenFile(userFile, os.O_CREATE|os.O_APPEND|os.O_RDWR, 0660)
	defer fout.Close()
	if err != nil {
		logger.Warn("open stats file fail, err:%s", err)
		return
	}

	monitor_tmp := Monitor{
		ReqCount:  0,
		FailCount: 0,
	}

	var count int64

	for {

		count = monitor.ReqCount - monitor_tmp.ReqCount
		if count == 0 {
			time.Sleep((time.Duration)(monitor.PrintInterval) * time.Second)
			continue
		}

		fmt.Fprintf(fout, "\n%s\n", time.Now().String())
		fmt.Fprintf(fout, "ReqCount:    %d\n", monitor.ReqCount)
		fmt.Fprintf(fout, "FailCount:   %d\n", monitor.FailCount)

		time.Sleep((time.Duration)(monitor.PrintInterval) * time.Second)
	}

	logger.Warn("exit stats")
}
