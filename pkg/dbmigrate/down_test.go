package dbmigrate

import (
	"database/sql"
	"testing"

	"github.com/franela/goblin"
)

func Test_MigrateDown(t *testing.T) {
	g := goblin.Goblin(t)
	loadFixtures()

	var db *sql.DB
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
				var res sql.NullString
				err := db.QueryRow("select name from sqlite_master where type = 'table' and name = ?", t).Scan(&res)
				g.Assert(err).Eql(sql.ErrNoRows)
			}

			var count int
			err = db.QueryRow("select count(*) from migration_history").Scan(&count)
			if err != nil {
				g.Fail(err)
			}

			g.Assert(count).Equal(0)
		})
	})
}
