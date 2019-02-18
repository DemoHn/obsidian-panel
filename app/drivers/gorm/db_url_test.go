package gorm

import (
	"testing"

	"github.com/DemoHn/obsidian-panel/infra"

	// goblin
	. "github.com/franela/goblin"
)

func TestGenerateDbUrl(t *testing.T) {
	g := Goblin(t)

	var inf *infra.Infrastructure
	g.Describe("GenerateDburl()", func() {

		g.It("should work /type = mysql", func() {
			inf = infra.NewForTest()
			// load default config
			inf.GetConfig().LoadDefault(map[string]interface{}{
				"database.type":     "mysql",
				"database.user":     "DemoHn",
				"database.password": "helloworld",
				"database.host":     "127.0.0.1",
				"database.port":     3307,
				"database.name":     "main_db",
				"database.options": map[interface{}]interface{}{
					"man": "kind",
				},
			})

			dbURL, err := GenerateDatabaseURL(inf)
			if err != nil {
				g.Fail(err)
			}

			g.Assert(dbURL).Equal("DemoHn:helloworld@tcp(127.0.0.1:3307)/main_db?man=kind")
		})

		g.It("should work /type = sqlite", func() {
			inf = infra.NewForTest()
			// load default config
			inf.GetConfig().LoadDefault(map[string]interface{}{
				"database.type": "sqlite",
				"database.path": "/tmp/main.db",
			})

			dbURL, err := GenerateDatabaseURL(inf)
			if err != nil {
				g.Fail(err)
			}

			g.Assert(dbURL).Equal("/tmp/main.db")
		})

		g.It("should fail /no available type", func() {
			inf = infra.NewForTest()
			// load default config
			inf.GetConfig().LoadDefault(map[string]interface{}{
				"database.type": "other_type",
			})

			_, err := GenerateDatabaseURL(inf)
			g.Assert(err != nil).Equal(true)
		})
	})
}
