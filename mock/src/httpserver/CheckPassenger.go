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

type CheckPassengerRequest struct {
	id      int
	dtags   string
	caller  string
	traceid string
	spanid  string
}

type CheckPassengerResponse struct {
	Error  *Errno      `json:"error"`
	Status int         `json:"status"`
	Value  *PassStatus `json:"value"`
}
type Errno struct {
}
type PassStatus struct {
	SecondNewUserTags  bool `json:"14688"`
	CoreUserTags       bool `json:"8284"`
	TreatmentUserTags1 bool `json:"8600"`
	TreatmentUserTags2 bool `json:"8602"`
	TreatmentUserTags3 bool `json:"8628"`
	TreatmentUserTags4 bool `json:"8630"`
}

func HandleCheckPassenger(w http.ResponseWriter, r *http.Request, logid int64) {
	monitor.InfoImpl.AddReqCount(global.DCHECKPASSEN)
	begintime := time.Now()

	r.ParseForm()
	passengeid := strings.TrimSpace(r.FormValue("id"))
	logger.Info("CheckPassenger, passengerid:%+v", passengeid)

	response := &CheckPassengerResponse{
		Error:  &Errno{},
		Status: 10000,
		Value:  &PassStatus{},
	}

	if err := CheckPassenger(passengeid, response, logid); err != nil {
		return
	}
	jsonString, err := json.Marshal(response)
	if err != nil {
		logger.Error("HandledCheckPassenger Marshal response failed,logid:%d,err:%s,response:%+v", logid, err.Error, response)
	}
	//logger.Info("HandledCheckDriver logid:%d, request:%+v,reponse:%+v", logid, request, response)
	logger.Info("lisiqi jsonResp:%v", jsonString)

	io.WriteString(w, string(jsonString))
	duration := time.Since(begintime)
	monitor.InfoImpl.AddProcessCostTime(global.DCHECKPASSEN, int64(duration/time.Microsecond))
	return
}

func CheckPassenger(passengerid string, response *CheckPassengerResponse, logid int64) error {
	pid, _ := strconv.Atoi(passengerid)
	/*passstatus := PassStatus{
		secondNewUserTags:  false,
		coreUserTags:       false,
		treatmentUserTags1: false,
		treatmentUserTags2: false,
		treatmentUserTags3: false,
		treatmentUserTags4: false,
	}*/
	passstatus := &PassStatus{}
	if pid%4 == 0 {
		passstatus.SecondNewUserTags = true
	} else if pid%4 == 1 {
		passstatus.CoreUserTags = true
	} else if pid%4 == 2 {
		passstatus.TreatmentUserTags1 = true
	} else {
	}
	response.Value = passstatus
	logger.Info("lisiqi,passstatus:%+v,value:%+v", passstatus, response.Value)
	logger.Info("CheckPassenger, logid:%d, passengerid:%+v,response:%+v", logid, passengerid, response)
	return nil
}
