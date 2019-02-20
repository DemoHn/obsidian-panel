package master

import (
	"os"
	"syscall"

	"github.com/DemoHn/obsidian-panel/pkg/apm/instance"
	"github.com/DemoHn/obsidian-panel/pkg/cmdspliter"

	"github.com/DemoHn/obsidian-panel/pkg/cfgparser"
)

// Master - the only one master that controls all instances
type Master struct {
	debugMode bool
	rpc       *rpcServer
	instances *instanceMap
}

var master *Master

// New -
func New(debugMode bool) *Master {
	master = &Master{
		debugMode: debugMode,
	}
	return master
}

// Init -
func (m *Master) Init(sockFile string) error {
	var err error
	// init RPC first
	if m.rpc, err = m.initRPC(sockFile); err != nil {
		return err
	}

	// init instance map to add/del instances
	return m.initInstanceMap()
}

// StartInstance - create & start instance
func (m *Master) StartInstance(req *StartInstanceRequest) (*instance.Instance, error) {
	prog, args, err := cmdspliter.SplitCommand(req.Command)
	if err != nil {
		return nil, err
	}
	// create instance
	inst := instance.New(prog, args, req.AutoRestart)
	err2 := m.addInstance(req.Name, inst)
	if err2 != nil {
		return nil, err2
	}
	// start instnace - non-blocking
	e := inst.Start()
	return inst, e
}

// StopInstance - stop instance
// Notice: still should wait for
func (m *Master) StopInstance(id int) (*instance.Instance, error) {
	var err error
	var inst *instance.Instance
	if inst, err = m.findInstance(id); err != nil {
		return nil, err
	}

	if err = inst.Stop(syscall.SIGTERM); err != nil {
		return nil, err
	}

	return inst, nil
}

// RestartInstance - find & restart instance
func (m *Master) RestartInstance(id int) (*instance.Instance, error) {
	var err error
	var inst *instance.Instance
	if inst, err = m.findInstance(id); err != nil {
		return nil, err
	}

	if err = inst.Restart(syscall.SIGTERM); err != nil {
		return nil, err
	}

	return inst, nil
}

// GetOneInstance - get instance
func (m *Master) GetOneInstance(id int) *instance.Instance {
	var err error
	var inst *instance.Instance

	if inst, err = m.findInstance(id); err != nil {
		return nil
	}

	return inst
}

// GetInstancesByFilter -
func (m *Master) GetInstancesByFilter(req *ListInstanceRequest) []*instance.Instance {
	return m.findInstancesByFilter(req.ID, req.Name)
}

// Listen to the sockFile
func (m *Master) Listen() error {
	return m.rpc.Listen()
}

// Teardown - teardown data
func (m *Master) Teardown(config *cfgparser.Config) error {
	var err error

	var pidFile string
	if pidFile, err = config.FindString("global.pidFile"); err != nil {
		return err
	}
	// 1. stop all instances - TODO
	// 2. close the RPC server
	if err = m.rpc.Shutdown(); err != nil {
		return err
	}
	// 3. delete pidFile
	return os.Remove(pidFile)
}
