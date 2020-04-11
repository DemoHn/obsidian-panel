package dbmigrate

import (
	"database/sql"
	"testing"

	"github.com/franela/goblin"
)

func Test_MigrationUp(t *testing.T) {
	g := goblin.Goblin(t)
	loadFixtures()

	var db *sql.DB
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
				var res string
				err := db.QueryRow("select name from sqlite_master where type = 'table' and name = ?", t).Scan(&res)
				if err != nil {
					g.Fail(err)
				}
				g.Assert(res).Eql(t)
			}

			// check migration_history
			var expHistory = []string{"01_A", "02_B", "03_C"}
			var histories = []string{}
			rows, err := db.Query("select version from migration_history")

			if err != nil {
				g.Fail(err)
			}

			for rows.Next() {
				var history string
				if err = rows.Scan(&history); err != nil {
					g.Fail(err)
				}

				histories = append(histories, history)
			}

			for k, v := range expHistory {
				g.Assert(v).Eql(histories[k])
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
