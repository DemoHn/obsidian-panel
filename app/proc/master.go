package proc

import (
	"net"
	"net/http"
	"net/rpc"
	"os"
)

// Master - masters all processes
type Master struct {
	sockFile string
	server   *http.Server
	workers  map[string]string
}

// NewMaster - new master controller
func NewMaster(sockFile string) (*Master, error) {
	master := &Master{
		sockFile: sockFile,
		workers:  map[string]string{},
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

// Listen - listen to corresponding file
func Listen(master *Master, done chan<- bool) error {
	// I. delete old sockFile
	// ignore errors here
	os.Remove(master.sockFile)

	l, err := net.Listen("unix", master.sockFile)
	if err != nil {
		return err
	}
	// send signal to chan
	done <- true
	return master.server.Serve(l)
}
