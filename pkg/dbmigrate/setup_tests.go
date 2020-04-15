package dbmigrate

import (
	"database/sql"
	"os"

	// import sqlite3
	_ "github.com/mattn/go-sqlite3"
)

type sqlFixture struct {
	version string
	upSQL   string
	downSQL string
}

// only on *ix and for sqlite/mysql
const sqliteFile = "/tmp/dbmigrate_test_12138.sql"

var fixtures = []sqlFixture{
	{
		version: "01_A",
		upSQL:   "create table table_01(id integer, name string)",
		downSQL: "drop table table_01",
	},
	{
		version: "02_B",
		upSQL:   "create table table_02(id integer, name string)",
		downSQL: "drop table table_02",
	},
	{
		version: "03_C",
		upSQL:   "create table table_03(id integer, name string)",
		downSQL: "drop table table_03",
	},
}

func setup() *sql.DB {
	db, _ := sql.Open("sqlite3", sqliteFile)
	return db
}

func teardown(db *sql.DB) {
	db.Close()
	os.Remove(sqliteFile)
}

func loadFixtures() {
	// clear global variable
	gMigrations = []*Migration{}
	// load fixtures
	for _, fixture := range fixtures {
		upSQL := fixture.upSQL
		downSQL := fixture.downSQL
		AddMigration(fixture.version, func(db *sql.DB) error {
			_, err := db.Exec(upSQL)
			return err
		}, func(db *sql.DB) error {
			_, err := db.Exec(downSQL)
			return err
		})
	}
}
