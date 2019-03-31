package sqlite

import (
	"database/sql"

	"github.com/DemoHn/obsidian-panel/infra"

	sqlmock "github.com/DATA-DOG/go-sqlmock"
	// import sqlite3
	_ "github.com/mattn/go-sqlite3"
)

// Driver - sqlite driver wraps sqlite
type Driver struct {
	*sql.DB
}

// New - new SQL driver
func New(config *infra.Config) (*Driver, error) {
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

// NewMock - new mock driver to help writing testcases
func NewMock() (*Driver, sqlmock.Sqlmock, error) {
	db, mock, err := sqlmock.New()
	if err != nil {
		return nil, nil, err
	}
	return &Driver{db}, mock, nil
}
