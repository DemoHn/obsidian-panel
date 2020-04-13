package migrations

import (
	"database/sql"
	"fmt"

	"github.com/DemoHn/obsidian-panel/pkg/dbmigrate"
)

const (
	configTableName = "obs_config"
	keyIndexName    = "only_one_config_key"
)

func init() {
	dbmigrate.AddMigration("20200413233928_create_config_schema", UpT20200413233928, DownT20200413233928)
}

// UpT20200413233928 - migration up script
func UpT20200413233928(db *sql.DB) error {
	var createStmt = fmt.Sprintf(`create table %s (
		id integer primary key autoincrement,
		key text not null,
		value text not null,
		type_hint integer not null    -- 1 -> int, 2 -> plain str, 3 -> bool, 14 -> csv(int), 24 -> csv(str)
	)`, configTableName)
	// Add Up Logic Here!
	if _, err := db.Exec(createStmt); err != nil {
		return err
	}

	var createIndexStmt = fmt.Sprintf("create unique %s on %s (key)", keyIndexName, configTableName)
	if _, err := db.Exec(createIndexStmt); err != nil {
		return err
	}
	return nil
}

// DownT20200413233928 - migration down script
func DownT20200413233928(db *sql.DB) error {
	// Add Down Logic Here!
	var dropIndexStmt = fmt.Sprintf("drop index %s", keyIndexName)
	if _, err := db.Exec(dropIndexStmt); err != nil {
		return err
	}
	var dropTableStmt = fmt.Sprintf("drop table %s", configTableName)
	if _, err := db.Exec(dropTableStmt); err != nil {
		return err
	}
	return nil
}
