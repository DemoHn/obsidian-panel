package dbmigrate

import (
	"testing"

	"github.com/franela/goblin"
	"github.com/jinzhu/gorm"
)

func Test_MigrateDown(t *testing.T) {
	g := goblin.Goblin(t)
	loadFixtures()

	var db *gorm.DB
	g.Describe("dbmigrate: Down()", func() {
		g.Before(func() {
			db = setup()
			if err := Up(db); err != nil {
				g.Fail(err)
			}
		})

		g.After(func() {
			teardown(db)
		})

		g.It("should migrate down all", func() {
			var err error
			if err = Down(db); err != nil {
				g.Fail(err)
			}

			// check if 3 tables are cleared
			var expTables = []string{"table_01", "table_02", "table_03"}
			for _, t := range expTables {
				hasTable := db.HasTable(t)
				g.Assert(hasTable).Eql(false)
			}

			// ensure no data in migration_histories
			var histories = []struct {
				Version string
			}{}
			if err = db.Raw("select version from migration_histories").Scan(&histories).Error; err != nil {
				g.Fail(err)
			}

			g.Assert(len(histories)).Equal(0)
		})
	})
}
