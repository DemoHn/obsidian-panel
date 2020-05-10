package proc

import (
	"fmt"
	"net"
	"net/http"
	"net/rpc"
	"os/exec"
	"syscall"
	"time"

	"github.com/DemoHn/obsidian-panel/infra"
)

// Master - masters all processes
type Master struct {
	sockFile  string
	rootPath  string
	server    *http.Server
	instances map[string]Instance
	workers   map[string]*exec.Cmd
}

// NewMaster - new master controller
func NewMaster(sockFile string, rootPath string) (*Master, error) {
	master := &Master{
		sockFile:  sockFile,
		rootPath:  rootPath,
		instances: map[string]Instance{},
		workers:   map[string]*exec.Cmd{},
		server:    new(http.Server),
	}
	// check rootPath
	if rootPath == "" {
		return nil, fmt.Errorf("rootPath of daemon should not be empty")
	}

	if err := rpc.Register(master); err != nil {
		return nil, err
	}
	rpc.HandleHTTP()
	return master, nil
}

// Echo - output exactly what input (usually for ping test)
func (m *Master) Echo(input string, out *string) error {
	*out = input
	return nil
}

// Sync - sync instance configurations
func (m *Master) Sync(input []InstanceReq, out *DataRsp) error {
	// copy instance
	for _, req := range input {
		nInst := Instance{
			name:          req.Name,
			procSign:      req.ProcSign,
			command:       req.Command,
			directory:     req.Directory,
			env:           req.Env,
			autoStart:     req.AutoStart,
			autoRestart:   req.AutoRestart,
			maxRetry:      req.MaxRetry,
			stdoutLogFile: req.StdoutLogFile,
			stderrLogFile: req.StderrLogFile,
			protected:     false,
		}
		m.instances[req.ProcSign] = nInst
	}
	// TODO
	*out = rspOK(nil)
	return nil
}

// Start - start an instance
func (m *Master) Start(procSign string, out *StartRsp) error {
	// TODO
	inst, ok := m.instances[procSign]
	if !ok {
		return fmt.Errorf("process: %s not found", procSign)
	}
	cmd, err := StartInstance(m, inst)
	if err != nil {
		return err
	}
	// when cmd is not nil, the process is starting for the first time
	if cmd != nil {
		done := make(chan bool, 1)
		// wait 3 secs to see if process still exists, if so
		m.waitForRunning(inst, cmd, done)
		runOK := <-done
		if runOK {
			*out = StartRsp{
				ProcSign:   procSign,
				Pid:        cmd.Process.Pid,
				HasRunning: false,
			}
			return nil
		}
		return fmt.Errorf("process: %s exits too quickly", inst.procSign)
	}

	f := NewFFlags(m.rootPath)
	pid := f.ReadPid(procSign)
	*out = StartRsp{
		ProcSign:   procSign,
		Pid:        pid,
		HasRunning: true,
	}
	return nil
}

// Stop - stop an instance
func (m *Master) Stop(procSign string, out *StopRsp) error {
	rtnCode, err := StopInstance(m, procSign, syscall.SIGINT)
	if err != nil {
		return err
	}
	*out = StopRsp{
		ReturnCode: rtnCode,
		ProcSign:   procSign,
	}
	return nil
}

//// helpers
func (m *Master) waitForRunning(inst Instance, cmd *exec.Cmd, done chan<- bool) {
	infra.Log.Debugf("process %s: wait 3 sec for running", inst.procSign)
	// TODO - use instance config
	t := 3 * time.Second
	time.Sleep(t)

	// check pid
	if kerr := syscall.Kill(cmd.Process.Pid, syscall.Signal(0)); kerr != nil {
		done <- false
	} else {
		f := NewFFlags(m.rootPath)
		f.SetForRunning(inst.procSign, cmd.Process.Pid)
		done <- true
	}
}

// Listen - listen to corresponding file
func Listen(master *Master, done chan<- bool) error {
	l, err := net.Listen("unix", master.sockFile)
	if err != nil {
		return err
	}
	// send signal to chan
	done <- true
	return master.server.Serve(l)
}
