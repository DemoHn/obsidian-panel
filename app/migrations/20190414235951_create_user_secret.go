package migrations

import (
	"database/sql"
	"fmt"

	"github.com/DemoHn/obsidian-panel/pkg/dbmigrate"
)

const tableName = "user_secrets"

func init() {
	dbmigrate.AddMigration("20190414235951_create_user_secret", UpT20190414235951, DownT20190414235951)
}

// UpT20190414235951 - migration up script
func UpT20190414235951(db *sql.DB) error {
	var err error

	var createTableStmt = fmt.Sprintf(`create table %s (
		id integer primary key autoincrement,
		account_id integer not null unique,
		public_key blob not null
	)`, tableName)

	if _, err = db.Exec(createTableStmt); err != nil {
		return err
	}
	return nil
}

// DownT20190414235951 - migration down script
func DownT20190414235951(db *sql.DB) error {
	var err error
	var stmt = fmt.Sprintf("drop table %s", tableName)
	if _, err = db.Exec(stmt); err != nil {
		return err
	}
	return nil
}
