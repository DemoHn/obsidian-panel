//go:generate protoc -I ../../protos/echo --go_out=plugins=grpc:../../protos/echo ../../protos/echo/echo.proto

// Package grpc ...
package grpc

import (
	"context"

	pb "github.com/DemoHn/obsidian-panel/app/protos/echo"
)

type echoServer struct{}

// Echo receives the input and reflect the same data back
func (es *echoServer) Echo(ctx context.Context, in *pb.EchoPayload) (*pb.EchoPayload, error) {
	return &pb.EchoPayload{
		Info: in.Info,
	}, nil
}

func registerEchoServer(d *Driver) {
	pb.RegisterEchoServiceServer(d.GetServer(), &echoServer{})
}
