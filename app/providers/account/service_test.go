package account

import (
	"testing"

	"github.com/DemoHn/obsidian-panel/infra"

	// goblin
	. "github.com/franela/goblin"
	"github.com/golang/mock/gomock"
)

func TestAccountService(t *testing.T) {
	g := Goblin(t)

	var ctrl *gomock.Controller
	var m *MockRepository
	var p *provider

	g.Describe("AccountService", func() {
		g.Before(func() {
			ctrl = gomock.NewController(t)
			m = NewMockRepository(ctrl)
			p = &provider{
				Infrastructure: infra.NewForTest(),
				repo:           m,
			}
		})

		g.After(func() {
			ctrl.Finish()
		})

		g.It("should register admin", func() {
			expName := "Name"

			m.EXPECT().InsertAccountData(expName, gomock.Any(), ADMIN).Return(&Model{
				Name:      expName,
				PermLevel: ADMIN,
			}, nil)
			acct, err := p.RegisterAdmin(expName, "password")
			if err != nil {
				g.Fail(err)
			}

			g.Assert(acct.Name).Equal(expName)
			g.Assert(acct.PermLevel).Equal(ADMIN)
		})
	})
}
