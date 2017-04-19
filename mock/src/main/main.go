/*
   Main模块
*/
package main

import (
	"fmt"
	"net/http"
	_ "net/http/pprof"
	"runtime"
	"runtime/debug"
	"sync"
	"time"

	"global"
	logger "helper/xlog4go"
	"httpserver"
	"monitor"

	gcfg "code.google.com/p/gcfg"
)

func main() {
	runtime.GOMAXPROCS(runtime.NumCPU())
	if err := initLog(); err != nil {
		fmt.Errorf("Failed to initialize logger, err: %s\n", err.Error())
		return
	}
	defer logger.Close()

	if err := initConf(); err != nil {
		logger.Error("init conf failed,err:%s", err.Error())
		return
	}

	// set recover
	defer func() {
		if err := recover(); err != nil {
			logger.Error("abort, unknown error, reason:%v, stack:%s",
				err, string(debug.Stack()))
		}
	}()

	initMonitor()

	go signal_proc()

	startPprof()
	go func() {
		httpserver.HttpInstance = httpserver.NewHttpServerInstance()
		err := httpserver.HttpInstance.Init()
		if err != nil {
			logger.Error("faled to start http service:%s", err.Error())
			global.StatQuitChan <- 1
		}
	}()

	value := <-global.StatQuitChan
	if value == 1 {
		logger.Warn("start http failed:value=%d", value)
	} else if value == 0 {
		logger.Info("driver-info quit:value=%d", value)
	}
	time.Sleep(5 * time.Second)
}

func initConf() error {
	if err := gcfg.ReadFileInto(&global.Conf, global.ConfFile); err != nil {
		logger.Error("read conf failed, err:%s", err.Error())
		return err
	}
	return nil

}

func initLog() error {
	if err := logger.SetupLogWithConf(global.LogFile); err != nil {
		fmt.Println("log init fail: %s", err.Error())
		return err
	}
	return nil
}

func startHttpServer() error {
	httpserver.HttpInstance = httpserver.NewHttpServerInstance()
	err := httpserver.HttpInstance.Init()
	if err != nil {
		logger.Error("faled to start http service:%s", err.Error())
		global.StatQuitChan <- 1
	}
	return nil
}

func startPprof() {
	go func() {
		err := http.ListenAndServe(":"+global.Conf.Server.PprofPort, nil)
		if err != nil {
			logger.Error("failed to start pprof monitor:%s", err.Error())
			return
		}
	}()
	return

}

func initMonitor() {
	monitor.TotalDataPool = &sync.Pool{New: func() interface{} {
		sendinfo := monitor.SendInfoData{}
		return &sendinfo
	}}
	monitor.InfoImpl = monitor.NewInfoResult()
	go monitor.InfoWorker()
}
