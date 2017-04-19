package main

/*
   中断信号的捕获函数
*/
import (
	"os"
	"os/signal"
	"syscall"

	"global"
	logger "helper/xlog4go"
	"httpserver"
)

func signal_proc() {

	logger.Info("start signal_proc")
	c := make(chan os.Signal, 1)

	signal.Notify(c, syscall.SIGUSR1)

	// Block until a signal is received.
	sig := <-c
	global.IsRunning = false

	logger.Info("Signal received: %v", sig)
	stopDynamicPriceGroupConsumer()
	stopGsApiGroupConsumer()
	httpserver.HttpInstance.Close()
	global.StatQuitChan <- 0
}

func stopGsApiGroupConsumer() {
	/*for _, groupConsumer := range consumer.GsOrderCreatedGroupConsumers {
		groupConsumer.Stop()
	}

	for _, groupConsumer := range consumer.GsOrderStrivedGroupConsumers {
		groupConsumer.Stop()
	}
	for _, groupConsumer := range consumer.GsOrderFinishedGroupConsumers {
		groupConsumer.Stop()
	}*/

}

func stopDynamicPriceGroupConsumer() {
	/*for _, groupConsumer := range consumer.DynamicPriceGroupConsumers {
		groupConsumer.Stop()
	}*/
}
