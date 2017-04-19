package common

import (
	"bytes"
	"encoding/base64"
	"fmt"
	"math"
	"math/rand"
	"path"
	"runtime"
	"strconv"
	"time"
)

func CallerName() string {
	var pc uintptr
	var file string
	var line int
	var ok bool
	if pc, file, line, ok = runtime.Caller(1); !ok {
		return ""
	}
	name := runtime.FuncForPC(pc).Name()
	res := "[" + path.Base(file) + ":" + strconv.Itoa(line) + "]" + name
	return res
}

var rand_gen = rand.New(rand.NewSource(time.Now().UnixNano()))

func RandInt() int {
	return rand_gen.Int()
}

func RandIntn(max int) int {
	return rand_gen.Intn(max)
}

func NowInS() int64 {
	return time.Now().Unix()
}

func NowInNs() int64 {
	return time.Now().UnixNano()
}

func NowInMs() int64 {
	return time.Now().UnixNano() / int64(time.Millisecond)
}

func UnixUsToTime(us int64) time.Time {
	second := int64(us / 1000000)
	nsecond := int64(us*1000 - second*1000000000)
	return time.Unix(second, nsecond)
}

func UnixToTime(ts int64) time.Time {
	t := time.Unix(ts, 0)
	return t
}

func UnixTimeStamp2Minute(ts int64) string {
	t := time.Unix(ts, 0)
	minute := fmt.Sprintf("%d%02d%02d%02d%02d", t.Year(), t.Month(), t.Day(), t.Hour(), t.Minute())
	return minute
}

func UnixTimeStamp2Hour(ts int64) string {
	t := time.Unix(ts, 0)
	hour := fmt.Sprintf("%d%02d%02d%02d", t.Year(), t.Month(), t.Day(), t.Hour())
	return hour
}

func MinuteToTime(minute string) time.Time {
	var (
		year  int
		month int
		day   int
		hour  int
		min   int
	)
	fmt.Sscanf(minute, "%4d%2d%2d%2d%2d", &year, &month, &day, &hour, &min)
	newTime := fmt.Sprintf("%04d-%02d-%02d %02d:%02d:00", year, month, day, hour, min)
	return StringToTime(newTime)
}

func HourToTime(hour string) time.Time {
	var (
		year  int
		month int
		day   int
		h     int
	)
	fmt.Sscanf(hour, "%4d%2d%2d%2d", &year, &month, &day, &h)
	newTime := fmt.Sprintf("%04d-%02d-%02d %02d:00:00", year, month, day, h)
	return StringToTime(newTime)
}

//将2006-01-02 15:04:05格式的字符串转成Time
func StringToTime(timestring string) time.Time {
	withNanos := "2006-01-02 15:04:05"
	loc, _ := time.LoadLocation("Asia/Shanghai")
	t, _ := time.ParseInLocation(withNanos, timestring, loc)
	return t
}

func GetMinute(t time.Time) string {
	minute := fmt.Sprintf("%d%02d%02d%02d%02d", t.Year(), t.Month(), t.Day(), t.Hour(), t.Minute())
	return minute
}

func GetDate(t time.Time) string {
	date := fmt.Sprintf("%d%02d%02d", t.Year(), t.Month(), t.Day())
	return date
}

//返回YYYY-MM-DD hh:mm:ss
func GetEsDate(t time.Time) string {
	date := fmt.Sprintf("%d-%02d-%02d %02d:%02d:%02d", t.Year(), t.Month(), t.Day(), t.Hour(), t.Minute(), t.Second())
	return date
}

//返回YYYYMMDDhh
func GetDateHour(t time.Time) string {
	date := fmt.Sprintf("%d%02d%02d%02d", t.Year(), t.Month(), t.Day(), t.Hour())
	return date
}

func Int64ArrayToString(nums []int64, serprater string) string {
	if len(nums) == 0 {
		return ""
	}
	var buffer bytes.Buffer
	for _, num := range nums {
		buffer.WriteString(strconv.FormatInt(num, 10))
		buffer.WriteString(serprater)

	}
	return buffer.String()
}

func Abs(x int32) int32 {
	switch {
	case x < 0:
		return -x
	case x == 0:
		return 0 // return correctly abs(-0)
	}
	return x
}

func Distance(flat float64, flng float64,
	tlat float64, tlng float64) (r int32) {
	distance := math.Sqrt((flat-tlat)*(flat-tlat) + (flng-tlng)*(flng-tlng))
	return int32(distance * 100000)
}

//根据高位订单id输出区号和低位订单id
func GetLowIntOrderId(CompOid int64) (int64, int64) {
	return ((CompOid >> 32) & 0xFFFFFFFF), (CompOid & 0xFFFFFFFF)
}

//对decode过的订单id解码
func DecodeOrderId(encodedOrderId string) (int64, error) {
	data1, err := base64.StdEncoding.DecodeString(encodedOrderId)
	if err != nil {
		return -1, err
	}
	data2, err := base64.StdEncoding.DecodeString(string(data1))
	if err != nil {
		return -1, err
	}
	oidInt64, _ := strconv.ParseInt(string(data2), 10, 64)
	return oidInt64, nil
}
