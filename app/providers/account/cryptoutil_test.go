package account

import (
	"crypto/subtle"
	"testing"

	// goblin
	. "github.com/franela/goblin"
)

func TestCryptoUtil(t *testing.T) {
	g := Goblin(t)

	g.Describe("CryptoUtil", func() {
		g.It("should generate different hashKeys /same passphase", func() {
			passphase := "hongkongjournalist"
			hash1 := generatePasswordHash(passphase)
			hash2 := generatePasswordHash(passphase)

			g.Assert(subtle.ConstantTimeCompare(hash1, hash2) != 1).Equal(true)
			g.Assert(len(hash1)).Equal(len(hash2))
			g.Assert(len(hash1)).Equal(6 + 3 + 32 + 32)
		})

		g.It("should verify password /result = true", func() {
			passphase := "hongkongjournalist"
			hash1 := generatePasswordHash(passphase)
			g.Assert(verifyPasswordHash(hash1, passphase)).Equal(true)
		})

		g.It("should verify password /result = false", func() {
			passphase := "hongkongjournalist"
			hash1 := generatePasswordHash(passphase)
			anotherpassword := "helloworld"
			g.Assert(verifyPasswordHash(hash1, anotherpassword)).Equal(false)
		})
	})
}
