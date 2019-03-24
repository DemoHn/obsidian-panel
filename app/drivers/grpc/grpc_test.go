package grpc

import (
	"context"
	"fmt"
	"testing"
	"time"

	// goblin
	. "github.com/franela/goblin"

	pb "github.com/DemoHn/obsidian-panel/app/protos/echo"
	grpcI "google.golang.org/grpc"
)

func TestGRPC(t *testing.T) {
	g := Goblin(t)

	g.Describe("Driver > GRPC", func() {
		expHost := "127.0.0.1"
		expPort := 12139
		grpcHandler, _ := New(expHost, expPort)
		g.Before(func() {
			go func() {
				if err := grpcHandler.Listen(); err != nil {
					g.Fail(err)
				}
			}()
			// wait for 200ms to continue
			<-time.After(200 * time.Millisecond)
		})

		g.After(func() {
			grpcHandler.Close()
		})

		g.It("should return Echo() data /sync", func() {
			var err error
			var conn *grpcI.ClientConn
			if conn, err = grpcI.Dial(fmt.Sprintf("%s:%d", expHost, expPort), grpcI.WithInsecure()); err != nil {
				g.Fail(err)
			}
			defer conn.Close()

			client := pb.NewEchoServiceClient(conn)

			var expInput = "Hello World"
			var output *pb.EchoPayload
			if output, err = client.Echo(context.Background(), &pb.EchoPayload{Info: expInput}); err != nil {
				g.Fail(err)
			}

			g.Assert(output.Info).Eql(expInput)
		})
	})
}
