// Package dbmigrate parses & executes migrations from specific **Golang** resources, which can be compiled
// into the binary to database.
// This package is widely used in SQL schema initialization for brand new db.
package dbmigrate

import (
	"database/sql"
)

type migrationFunc func(db *sql.DB) error
type txCallback func(tx *sql.Tx) error

// Migration - defines the migration object that includes up & down operations
type Migration struct {
	Version string
	Up      migrationFunc
	Down    migrationFunc
}

// MigrationHistory - defines the db model of logging migrations
type MigrationHistory struct {
	ID      uint32
	Version string
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

func initMigrationTable(db *sql.DB) error {
	var err error
	// DB statements
	// db name: migration_history
	var createTableStmt = `create table if not exists 
	migration_history (
		id integer primary key autoincrement,
		version text not null
	)`

	if _, err = db.Exec(createTableStmt); err != nil {
		return err
	}
	return nil
}

func readMigrationTable(db *sql.DB, isAsc bool) ([]string, error) {
	var err error
	var versions []MigrationHistory
	var rows *sql.Rows

	var orderStr string
	if isAsc {
		orderStr = "id asc"
	} else {
		orderStr = "id desc"
	}

	// query data
	var queryStmt = `select id,version from migration_history order by ?`
	if rows, err = db.Query(queryStmt, orderStr); err != nil {
		return nil, err
	}

	for rows.Next() {
		var id uint32
		var version string
		if err = rows.Scan(&id, &version); err != nil {
			return nil, err
		}

		versions = append(versions, MigrationHistory{
			ID:      id,
			Version: version,
		})
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
func transaction(db *sql.DB, fn txCallback) error {
	var finish = false
	var err error

	// begin transaction
	tx, err := db.Begin()
	defer func() {
		if finish != true {
			tx.Rollback()
		}
	}()
	if err != nil {
		return err
	}
	// execute
	if err = fn(tx); err != nil {
		return err
	}
	// commit
	if err = tx.Commit(); err != nil {
		return err
	}
	// finish transaction
	finish = true
	return nil
}
