package master

import (
	"github.com/DemoHn/obsidian-panel/pkg/apm/instance"
)

// Tower receives and handles all incoming commands.Tower
// P.S.: The term "tower" derives from "Control Tower" in aviation.
type Tower struct {
	master *Master
}

// Ping - ping
func (t *Tower) Ping(req *PingRequest, resp *PingResponse) error {
	resp.Info = "pong"
	return nil
}

// StartInstance - create & run an instance
func (t *Tower) StartInstance(req *StartInstanceRequest, resp *StartInstanceResponse) error {
	var err error
	var inst *instance.Instance

	master := t.master
	// If ID not nil, the first priority is to start existing instance
	if req.ID != nil {
		if inst, err = master.findInstance(*req.ID); err != nil {
			return err
		}
		inst.Start()
	} else {
		// start **new** instance
		if inst, err = master.StartInstance(req); err != nil {
			return err
		}
	}

	select {
	case e := <-inst.Once(instance.ActionStart):
		resp.IsSuccess = true
		resp.InstanceID = e.Int(0)
		resp.PID = e.Int(1)
	case e := <-inst.Once(instance.ActionError):
		resp.IsSuccess = false
		resp.InstanceID = e.Int(0)
		resp.Error = e.String(2)
	}

	return nil
}

// StopInstance -
func (t *Tower) StopInstance(req *StopInstanceRequest, resp *StopInstanceResponse) error {
	master := t.master
	inst, err := master.StopInstance(req.ID)
	if err != nil {
		return err
	}
	select {
	case e := <-inst.Once(instance.ActionStop):
		resp.IsSuccess = true
		resp.InstanceID = e.Int(0)
		resp.ExitCode = e.Int(1)
	case e := <-inst.Once(instance.ActionError):
		resp.IsSuccess = false
		resp.InstanceID = e.Int(0)
		resp.Error = e.String(2)
	}
	return nil
}

// RestartInstance -
func (t *Tower) RestartInstance(req *RestartInstanceRequest, resp *RestartInstanceResponse) error {
	var inst *instance.Instance
	var err error
	master := t.master

	if inst, err = master.RestartInstance(req.ID); err != nil {
		return err
	}

	select {
	case e := <-inst.Once(instance.ActionStop):
		resp.IsSuccess = true
		resp.InstanceID = e.Int(0)
	case e := <-inst.Once(instance.ActionError):
		resp.IsSuccess = false
		resp.InstanceID = e.Int(0)
		resp.Error = e.String(2)
	}
	return nil
}

// ListInstance -
func (t *Tower) ListInstance(req *ListInstanceRequest, resp *ListInstanceResponse) error {
	master := t.master
	var infos = []instance.Info{}
	insts := master.GetInstancesByFilter(req)
	for _, inst := range insts {
		infos = append(infos, inst.GetInfo())
	}

	resp.InstanceInfos = infos
	return nil
}
