package migrations

import (
	"database/sql"

	"github.com/DemoHn/obsidian-panel/pkg/dbmigrate"
)

func init() {
	dbmigrate.AddMigration("20190209212436_create_account", UpT20190209212436, DownT20190209212436)
}

// UpT20190209212436 - migration up script
func UpT20190209212436(db *sql.DB) error {
	// Add Up Logic Here!
	var err error

	var createTableStmt = `create table accounts (
		id integer primary key autoincrement,
		name text not null unique,
		credential blob not null,
		permission_level varchar(10) not null,
		created_at datetime not null,
		updated_at datetime not null 
	)`

	if _, err = db.Exec(createTableStmt); err != nil {
		return err
	}

	return nil
}

// DownT20190209212436 - migration down script
func DownT20190209212436(db *sql.DB) error {
	// Add Down Logic Here!
	var err error

	var deleteTableStmt = `drop table accounts`
	if _, err = db.Exec(deleteTableStmt); err != nil {
		return err
	}
	return nil
}
