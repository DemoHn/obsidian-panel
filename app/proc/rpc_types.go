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

// DataRsp - general data response
type DataRsp struct {
	Code    int
	Message string
	Data    map[string]interface{}
}
