package secret

import (
	// goblin

	"testing"

	. "github.com/franela/goblin"
)

func TestGenerateSecretKey(t *testing.T) {
	g := Goblin(t)

	g.Describe("genereate secret keypair", func() {
		g.It("should success generate keypair", func() {
			var bits = 2048
			_, _, err := generateRsaKeyPair(bits)
			if err != nil {
				g.Fail(err)
			}
		})
	})
}
