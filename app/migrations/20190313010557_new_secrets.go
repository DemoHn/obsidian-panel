package migrations

import (
	"database/sql"

	"github.com/DemoHn/obsidian-panel/pkg/dbmigrate"
)

func init() {
	dbmigrate.AddMigration("20190313010557_new_secrets", Up_20190313010557, Down_20190313010557)
}

// Up_20190313010557 - migration up script
func Up_20190313010557(db *sql.DB) error {
	// Add Up Logic Here!
	var err error

	var createTableStmt = `create table secrets (
		id integer primary key autoincrement,
		public_key blob not null,
		private_key blob not null,
		algorithm varchar(12) not null,
		active boolean
	)`
	if _, err = db.Exec(createTableStmt); err != nil {
		return err
	}
	return nil
}

// Down_20190313010557 - migration down script
func Down_20190313010557(db *sql.DB) error {
	// Add Down Logic Here!
	var err error
	if _, err = db.Exec("drop table secrets"); err != nil {
		return err
	}
	return nil
}
