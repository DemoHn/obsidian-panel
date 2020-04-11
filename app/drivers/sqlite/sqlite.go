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

// TransactionFunc - transaction function
type TransactionFunc func(tx *sql.Tx) error

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

// NewForTest - new SQL driver for testing usage, will accept a filepath
// as input parameter
func NewForTest(path string) (*Driver, error) {
	var db *sql.DB
	var err error
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

// Transaction - a wrapper for creating a transaction
func (drv *Driver) Transaction(fn TransactionFunc) error {
	tx, err := drv.Begin()
	if err != nil {
		return err
	}

	if err := fn(tx); err != nil {
		return tx.Rollback()
	}

	if err := tx.Commit(); err != nil {
		return tx.Rollback()
	}

	return nil
}
