package dbmigrate

import (
	"testing"

	"github.com/franela/goblin"
	"github.com/jinzhu/gorm"
)

func Test_MigrationUp(t *testing.T) {
	g := goblin.Goblin(t)
	loadFixtures()

	var db *gorm.DB
	g.Describe("dbmigrate: Up()", func() {
		g.Before(func() {
			db = setup()
		})

		g.After(func() {
			teardown(db)
		})

		g.It("should migrate all", func() {
			var err error
			if err = Up(db); err != nil {
				g.Fail(err)
			}

			// check if 3 tables are created
			var expTables = []string{"table_01", "table_02", "table_03"}
			for _, t := range expTables {
				hasTable := db.HasTable(t)
				g.Assert(hasTable).Eql(true)
			}

			// check migration_history
			var expHistory = []string{"01_A", "02_B", "03_C"}
			var histories = []struct {
				Version string
			}{}
			if err = db.Raw("select version from migration_histories").Scan(&histories).Error; err != nil {
				g.Fail(err)
			}

			for k, v := range expHistory {
				g.Assert(v).Eql(histories[k].Version)
			}
		})

		g.It("should migrate all /again", func() {
			var err error
			if err = Up(db); err != nil {
				g.Fail(err)
			}
		})
	})
}
