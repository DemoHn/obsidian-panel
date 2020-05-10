package proc

// InstanceReq - req instance data
type InstanceReq struct {
	ProcSign      string            `json:"procSign" validate:"required,proc_sign"`
	Name          string            `json:"name" validate:"required,max=50"`
	Command       string            `json:"command" validate:"required"`
	Directory     string            `json:"directory" validate:"-"`
	Env           map[string]string `json:"env"`
	AutoStart     bool              `json:"autoStart"`
	AutoRestart   bool              `json:"autoRestart"`
	StdoutLogFile string            `json:"stdoutLogFile"`
	StderrLogFile string            `json:"stderrLogFile"`
	MaxRetry      int               `json:"maxRetry"`
}

// StartRsp -
type StartRsp struct {
	ProcSign   string `json:"procSign"`
	Pid        int    `json:"pid"`
	HasRunning bool   `json:"hasRunning"`
}

// StopRsp - stop response
type StopRsp struct {
	ProcSign   string `json:"procSign"`
	ReturnCode int    `json:"returnCode"`
}

// DataRsp - general data response
type DataRsp struct {
	Code    int
	Message string
	Data    map[string]interface{}
}

func rspOK(data map[string]interface{}) DataRsp {
	return DataRsp{
		Code:    0,
		Message: "",
		Data:    data,
	}
}

func rspFail(code int, message string) DataRsp {
	return DataRsp{
		Code:    code,
		Message: message,
		Data:    map[string]interface{}{},
	}
}

// fail with data
func rspFailD(code int, message string, data map[string]interface{}) DataRsp {
	return DataRsp{
		Code:    code,
		Message: message,
		Data:    data,
	}
}
