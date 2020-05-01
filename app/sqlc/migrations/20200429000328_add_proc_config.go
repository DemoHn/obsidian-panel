package migrations

import (
	"database/sql"
	"fmt"

	"github.com/DemoHn/obsidian-panel/pkg/dbmigrate"
)

const pTableName = "proc_config"

func init() {
	dbmigrate.AddMigration("20200429000328_add_proc_config", UpT20200429000328, DownT20200429000328)
}

// UpT20200429000328 - migration up script
func UpT20200429000328(db *sql.DB) error {
	var createStmt = fmt.Sprintf(`create table %s (
		id integer primary key autoincrement,
		proc_sign text not null, -- unique sign to indicate the process, contains [a-ZA-Z0-9_-] only
		name text not null,
		command text not null, -- execution command (including exec file)
		directory text, -- working directory
		env text, -- environment variables, format: KEY1="val1",KEY2="val, val2"
		auto_start integer default '0' not null, -- start proc once daemon started
		auto_restart integer default '0' not null, -- restart proc when fails
		protected integer default '0' not null, -- if the proc config is unchangable, usually for system process
		stdout_logfile text,
		stderr_logfile text,
		max_retry integer default '0' not null -- max retry attempts since restart fails, 0 means unlimited
	)`, pTableName)
	if _, err := db.Exec(createStmt); err != nil {
		return err
	}

	var createIndexStmt = fmt.Sprintf("create unique index unique_proc_sign on %s (proc_sign)", pTableName)
	if _, err := db.Exec(createIndexStmt); err != nil {
		return err
	}
	return nil
}

// DownT20200429000328 - migration down script
func DownT20200429000328(db *sql.DB) error {
	// Add Down Logic Here!
	var dropIndexStmt = fmt.Sprintf("drop index unique_proc_sign")
	if _, err := db.Exec(dropIndexStmt); err != nil {
		return err
	}
	var dropTableStmt = fmt.Sprintf("drop table %s", pTableName)
	if _, err := db.Exec(dropTableStmt); err != nil {
		return err
	}
	return nil
}
