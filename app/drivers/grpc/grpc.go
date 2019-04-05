package grpc

import (
	"fmt"
	"net"

	grpcI "google.golang.org/grpc"
)

const (
	tcpNetwork = "tcp"
)

// Driver - grpc driver
type Driver struct {
	host       string
	port       int
	grpcServer *grpcI.Server
}

// New - new grpc driver (rpc handler, tcp server)
func New(host string, port int) (*Driver, error) {
	return &Driver{
		host:       host,
		port:       port,
		grpcServer: grpcI.NewServer(),
	}, nil
}

// GetServer - get grpc server instance for registeration
func (d *Driver) GetServer() *grpcI.Server {
	return d.grpcServer
}

// Listen - bind server to a port
func (d *Driver) Listen() error {
	var err error
	var l net.Listener
	url := fmt.Sprintf("%s:%d", d.host, d.port)

	// bind port
	if l, err = net.Listen(tcpNetwork, url); err != nil {
		return err
	}
	// register echo service (internal test service)
	registerEchoServer(d)
	// serve grpc protos
	if err = d.grpcServer.Serve(l); err != nil {
		return err
	}

	return nil
}

// Close - close a connection
func (d *Driver) Close() {
	d.grpcServer.GracefulStop()
}
