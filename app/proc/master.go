package proc

import (
	"fmt"
	"net"
	"net/http"
	"net/rpc"
	"syscall"
)

// Master - masters all processes
type Master struct {
	sockFile string
	rootPath string
	server   *http.Server
	workers  map[string]Instance
}

// NewMaster - new master controller
func NewMaster(sockFile string, rootPath string) (*Master, error) {
	master := &Master{
		sockFile: sockFile,
		rootPath: rootPath,
		workers:  map[string]Instance{},
		server:   new(http.Server),
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
		m.workers[req.ProcSign] = nInst
	}
	// TODO
	out = rspOK(nil)
	return nil
}

// Start - start an instance
func (m *Master) Start(procSign string, out *DataRsp) error {
	// TODO
	inst, ok := m.workers[procSign]
	if !ok {
		out = rspFail(-1, fmt.Sprintf("procSign: %s not found", procSign))
		return nil
	}
	if err := StartInstance(m.rootPath, inst); err != nil {
		return err
	}
	out = rspOK(nil)
	return nil
}

// Stop - stop an instance
func (m *Master) Stop(procSign string, out *DataRsp) error {
	if err := StopInstance(m, procSign, syscall.SIGTERM); err != nil {
		return err
	}
	out = rspOK(nil)
	return nil
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
