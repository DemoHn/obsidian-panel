package instance

import (
	"github.com/AlekSi/pointer"
	"github.com/DemoHn/obsidian-panel/pkg/apm/infra/logger"
	"github.com/DemoHn/obsidian-panel/pkg/apm/mod/process"
	"github.com/olebedev/emitter"
)

// Instance type defines a general instance type
type Instance struct {
	// ID - instance ID
	ID int
	// Name - instance name
	Name string
	// Path - instance command path
	Path string
	// Args - command arguments
	Args []string
	// AutoRestart - enable "AutoRestart" feature or not
	AutoRestart bool
	// command - process object
	command           process.IProcess
	status            *Status
	eventHandle       *EventHandle
	autoRestartHandle *AutoRestartHandle
}

var log *logger.Logger

// Info shows all informations
type Info struct {
	ID           int
	Name         string
	Status       StatusFlag
	RestartTimes int
	PID          *int
	// CPU time - in ratio * core
	CPU *float64
	// Memory occupied - in bytes
	Memory *int64
	// LaunchTime - in seconds
	LaunchTime *float64
}

// New apm instance (the basic unit of apm management, may contains multiple processes)
func New(path string, args []string, autoRestart bool) *Instance {
	log = logger.Get()
	inst := &Instance{
		Path:        path,
		Args:        args,
		AutoRestart: autoRestart,
		eventHandle: newEventHandle(),
		// initial status
		status:            initStatus(),
		autoRestartHandle: newAutoRestartHandle(),
	}

	return inst
}

// setters

// SetID -
func (inst *Instance) SetID(id int) {
	inst.ID = id
}

// SetName -
func (inst *Instance) SetName(name string) {
	inst.Name = name
}

// GetInfo - get current instance running information
func (inst *Instance) GetInfo() Info {
	status := inst.status
	command := inst.command
	info := Info{
		ID:           inst.ID,
		Name:         inst.Name,
		Status:       status.getStatus(),
		RestartTimes: status.getRestartCounter(),
		PID:          nil,
		CPU:          nil,
		Memory:       nil,
		LaunchTime:   nil,
	}

	if info.Status == StatusRunning {
		// pid
		var pid int
		pid = command.GetPID()
		info.PID = &pid

		pidusage := command.GetUsage()
		if pidusage != nil {
			info.CPU = pointer.ToFloat64(pidusage.CPU)
			info.Memory = pointer.ToInt64(pidusage.Memory)
			info.LaunchTime = pointer.ToFloat64(pidusage.Elapsed)
		}
	}
	return info
}

// Once - add listener to receive events
func (inst *Instance) Once(topic string) <-chan Event {
	eventHandle := inst.eventHandle
	return eventHandle.Once(topic, emitter.Sync)
}
