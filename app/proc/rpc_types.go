package proc

// InstanceReq - req instance data
type InstanceReq struct {
	ProcSign      string            `json:"procSign" validate:"required,proc_sign"`
	Name          string            `json:"name" validate:"required,max=50"`
	Command       string            `json:"command" validate:"required"`
	Directory     string            `json:"directory" validate:"-"`
	Env           map[string]string `json:"env"`
	AutoRestart   bool              `json:"autoRestart"`
	StdoutLogFile string            `json:"stdoutLogFile"`
	StderrLogFile string            `json:"stderrLogFile"`
	MaxRetry      int               `json:"maxRetry"`
}

// InstanceRsp -
type InstanceRsp struct {
	ProcSign      string            `json:"procSign"`
	Name          string            `json:"name"`
	Command       string            `json:"command"`
	Directory     string            `json:"directory"`
	Env           map[string]string `json:"env"`
	AutoRestart   bool              `json:"autoRestart"`
	StdoutLogFile string            `json:"stdoutLogFile"`
	StderrLogFile string            `json:"stderrLogFile"`
	MaxRetry      int               `json:"maxRetry"`
	Protected     bool              `json:"protected"`
	CreatedAt     int               `json:"createdAt"`
	UpdatedAt     int               `json:"updatedAt"`
}

// AddInstanceReq - add instance and start request
type AddInstanceReq struct {
	Override bool        `json:"override"`
	Instance InstanceReq `json:"instance"`
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

// InfoRsp - pid info
type InfoRsp struct {
	ProcSign string  `json:"procSign"`
	Pid      int     `json:"pid"`
	Status   int     `json:"status"`
	CPU      float64 `json:"cpu"`
	Memory   int64   `json:"memory"`
	Elapsed  int64   `json:"elapsed"`
}

// DataRsp - general data response
type DataRsp struct {
	Code    int
	Message string
	Data    map[string]interface{}
}

func exportInstanceFromReq(req InstanceReq) Instance {
	logFile := req.StdoutLogFile
	if logFile == "" {
		logFile = "$rootPath/$procSign.log"
	}
	errFile := req.StderrLogFile
	if errFile == "" {
		errFile = "$rootPath/$procSign.log"
	}

	return Instance{
		name:          req.Name,
		procSign:      req.ProcSign,
		command:       req.Command,
		directory:     req.Directory,
		env:           req.Env,
		autoRestart:   req.AutoRestart,
		maxRetry:      req.MaxRetry,
		stdoutLogFile: logFile,
		stderrLogFile: errFile,
		protected:     false,
	}
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
