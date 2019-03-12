package sqlite

import (
	"database/sql"
	// import sqlite3
	_ "github.com/mattn/go-sqlite3"
)

// Driver - sqlite driver wraps sqlite
type Driver struct {
	*sql.DB
}

// NewDriver - new SQL driver
func NewDriver(path string) (*Driver, error) {
	var err error
	var db *sql.DB
	if db, err = sql.Open("sqlite3", path); err != nil {
		return nil, err
	}

	return &Driver{db}, nil
}
