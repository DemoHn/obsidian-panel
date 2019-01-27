package main

import (
	"testing"

	"github.com/franela/goblin"
)

func TestExample(t *testing.T) {
	g := goblin.Goblin(t)

	g.Describe("Example", func() {
		g.It("250 + 250 = 500", func() {
			g.Assert(250 + 250).Equal(500)
		})
	})
}
