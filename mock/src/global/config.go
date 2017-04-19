package global

/*
   配置文件的结构体
*/

type Config struct {
	Server struct {
		GoRoutineNum      int
		Port              string
		PprofPort         string
		DataPath          string
		FeatureExpireTime int64
		CountExpireTime   int64
		ExpireTime        int64
	}
	Redis struct {
		Server           []string
		ConnectTimeoutMs int
		WriteTimeoutMs   int
		ReadTimeoutMs    int
		MaxIdle          int
		MaxActive        int
		IdleTimeoutS     int
		Password         string
		KeyPrefix        string
	}
	GroupConsumer map[string]*struct {
		GroupName string
		Topic     string
		Zookeeper string
		MsgType   string
		WorkerNum int
	}
	Worker map[string]*struct {
		WorkerNum    int
		TimeInterval int
	}
	DuseStatServer struct {
		Host           []string
		ConnectTimeout int
		ServerTimeout  int
		DriverNumUrl   string
		CityIdList     []int
	}
}
