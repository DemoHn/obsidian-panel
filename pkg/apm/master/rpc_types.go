package master

import (
	"github.com/DemoHn/obsidian-panel/pkg/apm/instance"
)

// StartInstanceRequest defines the input parameters of `Tower.StartInstance`
type StartInstanceRequest struct {
	Name        string
	Command     string
	AutoRestart bool
	ID          *int
}

// StartInstanceResponse defines the reply of `Tower.StartInstance`
type StartInstanceResponse struct {
	IsSuccess  bool
	Error      string
	InstanceID int
	PID        int
}

// StopInstanceRequest defines the input parameters of `Tower.StopInstance`
type StopInstanceRequest struct {
	ID int
}

// StopInstanceResponse defines the reply of `Tower.StopInstance`
type StopInstanceResponse struct {
	IsSuccess  bool
	ExitCode   int
	Error      string
	InstanceID int
}

// RestartInstanceRequest defines the input parameters of `Tower.StopInstance`
type RestartInstanceRequest struct {
	ID int
}

// RestartInstanceResponse defines the reply of `Tower.StopInstance`
type RestartInstanceResponse struct {
	IsSuccess  bool
	Error      string
	InstanceID int
}

// ListInstanceRequest defines the payload
type ListInstanceRequest struct {
	// ID - [optional]
	ID   *int
	Name *string
}

// ListInstanceResponse - response
type ListInstanceResponse struct {
	InstanceInfos []instance.Info
}

// PingRequest -
type PingRequest struct {
	Info string
}

// PingResponse -
type PingResponse struct {
	Info string
}
