// Package srpc (S-Remote Process Call) manages all RPC communications between
// client and server
package srpc

import (
	"context"
	"fmt"
	"net"
	"net/http"
	"net/rpc"

	"github.com/DemoHn/obsidian-panel/infra"
)

const (
	tcpNetwork string = "tcp"
)

var log = infra.GetMainLogger()

// Driver - srpc driver
type Driver struct {
	host       string
	port       int
	httpServer *http.Server
}

// New - new srpc driver (rpc handler, tcp server)
func New(host string, port int) *Driver {
	return &Driver{
		host:       host,
		port:       port,
		httpServer: &http.Server{},
	}
}

// Register - register receivers to serve rpc server
func (d *Driver) Register(receivers ...interface{}) error {
	var err error
	for _, recv := range receivers {
		if err = rpc.Register(recv); err != nil {
			return err
		}
	}

	return nil
}

// Listen - listen to server
func (d *Driver) Listen() error {
	var err error
	var l net.Listener
	url := fmt.Sprintf("%s:%d", d.host, d.port)

	rpc.HandleHTTP()
	// register RPC type receiver
	r := new(RPC)
	if err = d.Register(r); err != nil {
		return err
	}

	if l, err = net.Listen(tcpNetwork, url); err != nil {
		return err
	}
	return d.httpServer.Serve(l)
}

// Close - close the server to end serving rpc connections
func (d *Driver) Close() error {
	return d.httpServer.Shutdown(context.Background())
}
