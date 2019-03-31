package migrations

import (
	"database/sql"

	"github.com/DemoHn/obsidian-panel/pkg/dbmigrate"
)

func init() {
	dbmigrate.AddMigration("20190209212436_create_account", Up_20190209212436, Down_20190209212436)
}

// Up_20190209212436 - migration up script
func Up_20190209212436(db *sql.DB) error {
	// Add Up Logic Here!
	var err error

	var createTableStmt = `create table accounts (
		id integer primary key autoincrement,
		name text not null unique,
		credential blob not null,
		permission_level varchar(10) not null
	)`
	if _, err = db.Exec(createTableStmt); err != nil {
		return err
	}

	return nil
}

// Down_20190209212436 - migration down script
func Down_20190209212436(db *sql.DB) error {
	// Add Down Logic Here!
	var err error

	var deleteTableStmt = `drop table accounts`
	if _, err = db.Exec(deleteTableStmt); err != nil {
		return err
	}
	return nil
}
