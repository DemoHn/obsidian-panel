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
	return nil, nil
}

// Echo for test
func (m *Master) Echo(input string) string {
	return input
}

// Listen - listen to corresponding file
func Listen(master *Master) error {
	// I. delete old sockFile
	// ignore errors here
	os.Remove(master.sockFile)

	l, err := net.Listen("unix", master.sockFile)
	if err != nil {
		return err
	}

	return master.server.Serve(l)
}
