package instance

import (
	"github.com/olebedev/emitter"
)

// EventConfig defines all switches of a command that triggers
// the corresponding event
type EventConfig struct {
	OnStart      bool
	OnStop       bool
	OnStdinData  bool
	OnStdoutData bool
	OnStderrData bool
}

// EventHandle manages all events
type EventHandle struct {
	config *EventConfig
	*emitter.Emitter
}

// Event -
type Event = emitter.Event

// Action -
type Action = string

const (
	// ActionStart -
	ActionStart Action = "action_start"
	// ActionStop -
	ActionStop Action = "action_stop"
	// ActionRestart -
	ActionRestart Action = "action_restart"
	// ActionError -
	ActionError Action = "action_error"
)

// methods
func newEventHandle() *EventHandle {
	defaultEventConfig := &EventConfig{
		OnStart:      true,
		OnStop:       true,
		OnStdinData:  false,
		OnStdoutData: false,
		OnStderrData: false,
	}

	return &EventHandle{
		config:  defaultEventConfig,
		Emitter: &emitter.Emitter{},
	}
}

// Close - close all event listeners
func (handle *EventHandle) close() {
	handle.Emitter.Off("*")
}

// SendEvent - send corresponding event to instance
func (handle *EventHandle) sendEvent(action Action, inst *Instance, err error, args ...interface{}) {
	emitter := handle.Emitter

	// send error event with no other reasons
	if err != nil {
		// params: [id, action_name, error]
		emitter.Emit(ActionError, inst.ID, action, err.Error())
		return
	}
	// send concrete events
	switch action {
	case ActionStart:
		// make sure the command EXISTS!
		pid := inst.command.GetPID()
		// params: [id, pid]
		emitter.Emit(ActionStart, inst.ID, pid)
	case ActionStop:
		exitCode := 0
		exitArg := args[0]
		if code, ok := exitArg.(int); ok {
			exitCode = code
		}
		emitter.Emit(ActionStop, inst.ID, exitCode)
	}
}
