package srpc

import (
	"fmt"
	"net/rpc"
	"testing"
	"time"

	// goblin
	. "github.com/franela/goblin"
)

func TestSRPC(t *testing.T) {
	g := Goblin(t)

	g.Describe("Driver > SRPC", func() {
		expHost := "127.0.0.1"
		expPort := 12138
		rpcHandler := New(expHost, expPort)
		g.Before(func() {
			go func() {
				if err := rpcHandler.Listen(); err != nil {
					g.Fail(err)
				}
			}()
			// wait for 200ms to continue
			<-time.After(200 * time.Millisecond)
		})

		g.It("should return Echo() data /sync", func() {
			var client *rpc.Client
			var err error
			if client, err = rpc.DialHTTP("tcp", fmt.Sprintf("%s:%d", expHost, expPort)); err != nil {
				g.Fail(err)
			}

			var expInput = "Hello World"
			var expOutput string
			if err = client.Call("RPC.Echo", expInput, &expOutput); err != nil {
				g.Fail(err)
			}

			g.Assert(expOutput).Eql(expInput)
		})

		g.It("should return Echo() data /async", func() {
			var client *rpc.Client
			var err error
			if client, err = rpc.DialHTTP("tcp", fmt.Sprintf("%s:%d", expHost, expPort)); err != nil {
				g.Fail(err)
			}

			var expInput = "Hello World"
			var expOutput string
			call := client.Go("RPC.Echo", expInput, &expOutput, nil)
			// wait until done
			<-call.Done
			g.Assert(expOutput).Eql(expInput)
		})
	})
}
