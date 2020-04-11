package dbmigrate

import (
	"database/sql"
	"fmt"
	"sort"
)

// Up - Execute all pending migrations to up the version to the latest
func Up(db *sql.DB) error {
	var err error
	if err = initMigrationTable(db); err != nil {
		return fmt.Errorf("init migration table failed: %s", err.Error())
	}
	var versions []string
	if versions, err = readMigrationTable(db, true); err != nil {
		return fmt.Errorf("read migration table failed: %s", err.Error())
	}

	execMigrations := filterMigrations(versions, gMigrations, true)

	// sort migrations before running
	sort.SliceStable(execMigrations, func(i int, j int) bool {
		return execMigrations[i].Version < execMigrations[j].Version
	})

	if err = upMigrations(db, execMigrations); err != nil {
		return err
	}
	return nil
}

func upMigrations(db *sql.DB, migrations []*Migration) error {
	var err error
	for _, mg := range migrations {
		err = transaction(db, func(tx *sql.Tx) error {
			var e error
			if e = mg.Up(db); e != nil {
				return e
			}
			// add item to migration_history
			var createStmt = `insert into migration_history (version) values (?)`
			_, e = db.Exec(createStmt, mg.Version)
			return e
		})

		if err != nil {
			return fmt.Errorf("migration error on version[%s]: %s", mg.Version, err.Error())
		}
	}

	return nil
}
