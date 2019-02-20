package master

import (
	"context"
	"net"
	"net/http"
	"net/rpc"
)

// rpc_server: all about RPC server

const (
	unixNetwork string = "unix"
)

type rpcServer struct {
	sockFile   string
	httpServer *http.Server
}

func (m *Master) initRPC(sockFile string) (*rpcServer, error) {
	var err error
	tower := &Tower{
		master: m,
	}
	err = rpc.Register(tower)
	if err != nil {
		return nil, err
	}

	rpc.HandleHTTP()
	rpcN := &rpcServer{
		sockFile:   sockFile,
		httpServer: &http.Server{},
	}
	return rpcN, nil
}

func (r *rpcServer) Listen() error {
	var l net.Listener
	var err error

	if l, err = net.Listen(unixNetwork, r.sockFile); err != nil {
		return err
	}

	return r.httpServer.Serve(l)
}

func (r *rpcServer) Shutdown() error {
	return r.httpServer.Shutdown(context.Background())
}
