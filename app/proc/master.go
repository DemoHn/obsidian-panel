package proc

import (
	"net"
	"net/http"
	"net/rpc"
)

// Master - masters all processes
type Master struct {
	sockFile string
	rootPath string
	server   *http.Server
	workers  map[string]Instance
}

// NewMaster - new master controller
func NewMaster(sockFile string) (*Master, error) {
	master := &Master{
		sockFile: sockFile,
		workers:  map[string]Instance{},
		server:   new(http.Server),
	}

	if err := rpc.Register(master); err != nil {
		return nil, err
	}

	rpc.HandleHTTP()
	return master, nil
}

// Echo for test
func (m *Master) Echo(input string, out *string) error {
	*out = input
	return nil
}

// Sync - sync instance configurations
func (m *Master) Sync() error {
	// TODO
	return nil
}

// Start - start an instance
func (m *Master) Start(procSign string, out *string) error {
	// TODO
	return nil
}

// Stop - stop an instance
func (m *Master) Stop(procSign string, out *string) error {
	// TODO
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
