package instance

import (
	"os"
	"os/exec"
	"syscall"

	"github.com/DemoHn/obsidian-panel/pkg/apm/infra/logger"
	"github.com/DemoHn/obsidian-panel/pkg/apm/mod/process"
)

// control flow

// Start a registered instance
func (inst *Instance) Start() error {
	// pre-check
	go func() {
		var err error
		// create inst.command first
		inst.createProcess()
		if err = inst.start(); err != nil {
			return
		}
		// wait for process finish
		err = inst.wait()
		inst.afterWait(err)
		// close event handle
		inst.eventHandle.close()
	}()
	return nil
}

// Stop - stop instance.
// Notice: It will just send a SIGTERM signal to the running process
// and will not stop it immediately.
func (inst *Instance) Stop(signal os.Signal) error {
	autoRestartHandle := inst.autoRestartHandle

	// send stop signal
	autoRestartHandle.mask()
	return inst.stop(signal)
}

// ForceStop - stop the instance by force
func (inst *Instance) ForceStop() error {
	autoRestartHandle := inst.autoRestartHandle

	autoRestartHandle.mask()
	return inst.kill()
}

// Restart - restart the instance
func (inst *Instance) Restart(signal os.Signal) error {
	autoRestartHandle := inst.autoRestartHandle
	// acquire restart lock to make auto-restart work by force
	// it will be automatically released after tick()
	autoRestartHandle.forceRestart()
	return inst.stop(signal)
}

// internal methods
func (inst *Instance) createProcess() {
	cmd := process.New(inst.Path, inst.Args...)
	// TODO for debugging
	cmd.Stdin = os.Stdin
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	inst.command = cmd
}

func (inst *Instance) start() error {
	var err error
	log := logger.Get()
	cmd := inst.command
	status := inst.status
	eventHandle := inst.eventHandle
	autoRestartHandle := inst.autoRestartHandle
	// unmask to enable auto-restart again
	autoRestartHandle.unmask()

	log.Debugf("[apm] ID(%d) going to start", inst.ID)
	if err = cmd.Start(); err != nil {
		log.Debugf("[apm] ID(%d) start failed err=%s", inst.ID, err)
		eventHandle.sendEvent(ActionStart, inst, err)
		autoRestartHandle.tick(inst)
		return err
	}

	// send start event
	status.setStatus(StatusRunning)
	status.addRestartCounter()
	eventHandle.sendEvent(ActionStart, inst, err)
	log.Debugf("[apm] ID(%d) instance is running", inst.ID)
	return nil
}

func (inst *Instance) wait() error {
	cmd := inst.command
	return cmd.Wait()
}

func (inst *Instance) afterWait(err error) {
	log := logger.Get()
	status := inst.status
	eventHandle := inst.eventHandle
	autoRestartHandle := inst.autoRestartHandle

	log.Debugf("[apm] ID(%d) going to stop", inst.ID)
	status.setStatus(StatusStopped)
	autoRestartHandle.tick(inst)
	// if no error
	if err == nil {
		log.Debugf("[apm] ID(%d) stop succeed", inst.ID)
		eventHandle.sendEvent(ActionStop, inst, nil, 0)
		return
	}

	log.Debugf("[apm] ID(%d) stop with err=%s", inst.ID, err)
	// if err = *exec.ExitError, that means the process returned
	// with non-zero value
	if exitError, ok := err.(*exec.ExitError); ok {
		ws := exitError.Sys().(syscall.WaitStatus)
		exitCode := ws.ExitStatus()
		eventHandle.sendEvent(ActionStop, inst, nil, exitCode)
	} else {
		eventHandle.sendEvent(ActionStop, inst, err)
	}
}

func (inst *Instance) stop(signal os.Signal) error {
	return inst.command.Stop(signal)
}

func (inst *Instance) kill() error {
	return inst.command.Kill()
}
