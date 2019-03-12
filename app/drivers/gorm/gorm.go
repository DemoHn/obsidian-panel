package gorm

import (
	"os"
	"path/filepath"

	"github.com/jinzhu/gorm"

	// import sqlite3 dialect
	_ "github.com/jinzhu/gorm/dialects/sqlite"
	// import infra (config)
	"github.com/DemoHn/obsidian-panel/infra"
)

// Driver - gorm_driver is a wrapper of the popular ORM: gorm
type Driver struct {
	*gorm.DB
}

var config = infra.GetConfig()

// NewDriver - new gorm driver
func NewDriver() (*Driver, error) {
	var err error
	var db *gorm.DB
	var dbURL string

	// find dbURL first
	if dbURL, err = GenerateDatabaseURL(config); err != nil {
		return nil, err
	}

	// since we are using sqlite3, dbURL is just filepath
	// thus we have to mkdir -p of the folder
	os.MkdirAll(filepath.Dir(dbURL), os.ModePerm)
	// open db connection
	if db, err = gorm.Open("sqlite3", dbURL); err != nil {
		return nil, err
	}

	return &Driver{DB: db}, nil
}

// Transaction - wrap a SQL transaction
func (d *Driver) Transaction(fn func(tx *Driver) error) error {
	var finish = false
	var err error
	tx := &Driver{
		DB: d.Begin(),
	}
	defer func() {
		if finish != true {
			tx.Rollback()
		}
	}()
	if tx.Error != nil {
		return tx.Error
	}
	// execute
	if err = fn(tx); err != nil {
		return err
	}
	// commit
	if err = tx.Commit().Error; err != nil {
		return err
	}
	// finish transaction
	finish = true
	return nil
}

// GetDB - get raw gorm DB
func (d *Driver) GetDB() *gorm.DB {
	return d.DB
}
