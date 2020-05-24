package sqlc

import (
	"database/sql"

	"github.com/DemoHn/obsidian-panel/pkg/dbmigrate"
	// init migrations
	_ "github.com/DemoHn/obsidian-panel/app/sqlc/migrations"
)

// MigrateUp -
func MigrateUp(db *sql.DB) error {
	return dbmigrate.Up(db)
}

// MigrateDown -
func MigrateDown(db *sql.DB, step int) error {
	return dbmigrate.Down(db, step)
}

// MigrateInit -
func MigrateInit(db *sql.DB) (bool, error) {
	return dbmigrate.Init(db)
}
