package migrations

import (
	"database/sql"
	"fmt"

	"github.com/DemoHn/obsidian-panel/pkg/dbmigrate"
)

const ushTableName = "user_secrets_history"

func init() {
	dbmigrate.AddMigration("20190417005851_create_user_secret_history", Up_20190417005851, Down_20190417005851)
}

// Up_20190417005851 - migration up script
func Up_20190417005851(db *sql.DB) error {
	var err error

	var createTableStmt = fmt.Sprintf(`create table %s (
		id integer primary key autoincrement,
		account_id integer not null,
		action varchar(20) not null
		happened_at datetime not null
	)`, ushTableName)

	if _, err = db.Exec(createTableStmt); err != nil {
		return err
	}
	return nil
}

// Down_20190417005851 - migration down script
func Down_20190417005851(db *sql.DB) error {
	var err error
	var stmt = fmt.Sprintf("drop table %s", ushTableName)
	if _, err = db.Exec(stmt); err != nil {
		return err
	}
	return nil
}
