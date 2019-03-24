package sqlite

import (
	"database/sql"

	"github.com/DemoHn/obsidian-panel/infra"

	// import sqlite3
	_ "github.com/mattn/go-sqlite3"
)

// Driver - sqlite driver wraps sqlite
type Driver struct {
	*sql.DB
}

// NewDriver - new SQL driver
func NewDriver(config *infra.Config) (*Driver, error) {
	var err error
	var db *sql.DB
	var path string
	if path, err = config.FindString("database.path"); err != nil {
		return nil, err
	}

	if db, err = sql.Open("sqlite3", path); err != nil {
		return nil, err
	}

	return &Driver{db}, nil
}
