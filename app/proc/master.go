package proc

import (
	"fmt"
	"net"
	"net/http"
	"net/rpc"
	"os"
	"os/exec"
	"os/signal"
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
	pidInfo   map[string]PidInfo
}

// NewMaster - new master controller
func NewMaster(sockFile string, rootPath string) (*Master, error) {
	master := &Master{
		sockFile:  sockFile,
		rootPath:  rootPath,
		instances: map[string]Instance{},
		workers:   map[string]*exec.Cmd{},
		pidInfo:   map[string]PidInfo{},
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

// LoadConfig - load all instance configurations
func (m *Master) LoadConfig(input []InstanceReq, out *DataRsp) error {
	// copy instance
	for _, req := range input {
		nInst := exportInstanceFromReq(req)
		m.instances[req.ProcSign] = nInst
	}
	// TODO
	*out = rspOK(nil)
	return nil
}

// AddConfig -
func (m *Master) AddConfig(req AddInstanceReq, out *DataRsp) error {
	procSign := req.Instance.ProcSign

	_, exists := m.instances[procSign]
	if exists && !req.Override {
		return fmt.Errorf("process: %s has exists", procSign)
	}

	m.instances[procSign] = exportInstanceFromReq(req.Instance)
	*out = rspOK(nil)
	return nil
}

// AddAndStart - add instance and start it
// if same procSign has exists,
//   - override = true, stop old procSign, update with new instance and then start
//   - override = false, throw error
func (m *Master) AddAndStart(req AddInstanceReq, out *StartRsp) error {
	procSign := req.Instance.ProcSign

	_, exists := m.instances[procSign]
	if exists {
		if req.Override {
			_, err := StopInstance(m, procSign, syscall.SIGINT)
			if err != nil {
				return err
			}
		} else {
			return fmt.Errorf("process: %s has exists", procSign)
		}
	}
	// else: add instance and start
	nInst := exportInstanceFromReq(req.Instance)
	m.instances[procSign] = nInst
	// start
	return m.Start(procSign, out)
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

// Restart - stop & start an instance
func (m *Master) Restart(procSign string, out *StartRsp) error {
	// I. find instance
	inst, ok := m.instances[procSign]
	if !ok {
		return fmt.Errorf("process: %s not found", procSign)
	}
	// II. stop instance
	if _, err := stopInstance(m, inst, syscall.SIGINT); err != nil {
		// ignore "pid not found" error
		if err.Error() != "no active pid found" {
			return err
		}
	}
	NewFFlags(m.rootPath).SetForStopped(inst.procSign)
	// III. start instance
	return m.Start(procSign, out)
}

// GetInfo - get info of a procSign
func (m *Master) GetInfo(procSign string, out *InfoRsp) error {
	if err := m.updatePidInfo(procSign); err != nil {
		return err
	}
	info := m.pidInfo[procSign]

	*out = InfoRsp{
		ProcSign: procSign,
		Pid:      info.Pid,
		Elapsed:  info.Elapsed,
		Status:   info.Status,
		CPU:      info.CPU,
		Memory:   info.Memory,
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
	if !isPidRunning(cmd.Process.Pid) {
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
	go sigchldHandler(func(pid int) {
		f := NewFFlags(master.rootPath)
		// find instance of corresponding pid
		for procSign, w := range master.workers {
			if w.Process.Pid == pid {
				f.AddRetryCount(procSign)
				inst, ok := master.instances[procSign]
				// to prevent instances updated/deleted
				if ok {
					retryCount := f.ReadRetryCount(procSign)
					if inst.autoRestart && retryCount <= inst.maxRetry {
						go restartHandler(master, procSign)
						break
					}
				}
			}
		}
	})
	return master.server.Serve(l)
}

func sigchldHandler(callback func(int)) {
	sigchld := make(chan os.Signal, 1)
	// register SIGCHLD signal
	signal.Notify(sigchld, syscall.SIGCHLD)

	for {
		// wait for recving SIGCHLD signal to continue
		<-sigchld
		for {
			var waitStatus syscall.WaitStatus
			var rusage syscall.Rusage
			wpid, err := syscall.Wait4(-1, &waitStatus, syscall.WNOHANG, &rusage)
			// stop iteration if no such pid pending to wait
			if err != nil {
				break
			}

			callback(wpid)
		}
	}
}

// restartHandler -
func restartHandler(master *Master, procSign string) {
	// wait for 1 second to avoid restart too frequently
	time.Sleep(1 * time.Second)
	var out StartRsp
	// TODO: collect file
	master.Start(procSign, &out)
}
