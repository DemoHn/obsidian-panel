// Package dbmigrate parses & executes migrations from specific **Golang** resources, which can be compiled
// into the binary to database.
// This package is widely used in SQL schema initialization for brand new db.
package dbmigrate

import (
	"github.com/jinzhu/gorm"
)

type migrationFunc func(db *gorm.DB) error
type txCallback func(tx *gorm.DB) error

// Migration - defines the migration object that includes up & down operations
type Migration struct {
	Version string
	Up      migrationFunc
	Down    migrationFunc
}

// MigrationHistory - defines the db model of logging migrations
type MigrationHistory struct {
	ID      uint32 `gorm:"primary_key"`
	Version string `gorm:"type:text; not null" json:"version"`
}

var (
	// global Migrations value
	gMigrations = []*Migration{}
)

// AddMigration - add migration operations to the variable `migrations` from which
// up operation will analyse directly
func AddMigration(version string, up migrationFunc, down migrationFunc) {
	gMigrations = append(gMigrations, &Migration{
		Version: version,
		Up:      up,
		Down:    down,
	})
}

/*
// UpTo - up to a version
func UpTo(version string) error {

}

// DownTo - down to a version
func DownTo(version string) error {

}
*/

func initMigrationTable(db *gorm.DB) error {
	var err error
	if !db.HasTable(&MigrationHistory{}) {
		db = db.CreateTable(&MigrationHistory{})
		err = db.Error
	}

	return err
}

func readMigrationTable(db *gorm.DB, isAsc bool) ([]string, error) {
	var err error
	var versions []MigrationHistory

	var orderStr string
	if isAsc {
		orderStr = "id asc"
	} else {
		orderStr = "id desc"
	}
	if err = db.Order(orderStr).Find(&versions).Error; err != nil {
		return nil, err
	}
	// map results to ordered array of existing versions
	var versionArr = []string{}
	for _, v := range versions {
		versionArr = append(versionArr, v.Version)
	}

	return versionArr, nil
}

func filterMigrations(storedVersions []string, migrations []*Migration, exclude bool) []*Migration {
	var execMigrations = []*Migration{}
	// append available migrations
	for _, mg := range migrations {
		var included = false
		for _, v := range storedVersions {
			if mg.Version == v {
				included = true
				break
			}
		}

		// 1. When exclude = true, we expect to add migrations that are not
		// included in `storedVersions`, i.e. included = false
		// 2. When exclude = false, we expect to add migrations that are INSIDE
		// `storedVersions`, i.e. included = true
		if included != exclude {
			execMigrations = append(execMigrations, mg)
		}
	}

	return execMigrations
}

// helpers
func transaction(db *gorm.DB, fn txCallback) error {
	var finish = false
	var err error
	tx := db.Begin()
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
