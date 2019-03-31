//go:generate protoc -I ../../protos/account --go_out=plugins=grpc:../../protos/account ../../protos/account/login.proto

// Package account -
package account

import (
	"context"

	"github.com/DemoHn/obsidian-panel/app/drivers"

	pb "github.com/DemoHn/obsidian-panel/app/protos/account"
)

type rpcServer struct {
	*drivers.Drivers
	provider *iProvider
}

func (s *rpcServer) Login(ctx context.Context, in *pb.LoginPayload) (*pb.LoginReply, error) {
	jwt, err := s.provider.Login(in.Name, in.Password)
	if err != nil {
		return &pb.LoginReply{
			SuccessOrFail: &pb.LoginReply_Error{
				Error: &pb.ErrorReply{
					Name: err.Error(),
				},
			},
		}, nil
	}
	return &pb.LoginReply{
		SuccessOrFail: &pb.LoginReply_Resp{
			Resp: &pb.LoginResponse{
				Jwt: jwt,
			},
		},
	}, nil
}
