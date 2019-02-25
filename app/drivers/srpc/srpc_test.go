package srpc

import (
	"testing"

	// goblin
	. "github.com/franela/goblin"
)

func TestSRPC(t *testing.T) {
	g := Goblin(t)

	g.Describe("Driver > SRPC", func() {

		rpcHandler := New("", 12138)
		g.Before(func() {
			go func() {
				if err := rpcHandler.Listen(); err != nil {
					g.Fail(err)
				}
			}()
		})

		g.It("should Ping()", func() {

		})
	})
}
