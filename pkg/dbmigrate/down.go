package dbmigrate

import (
	"database/sql"
	"fmt"
)

// Down - down to lowest version
func Down(db *sql.DB, step int) error {
	var err error
	if err = initMigrationTable(db); err != nil {
		return fmt.Errorf("init migration table failed: %s", err.Error())
	}

	var versions []string
	if versions, err = readMigrationTable(db, false); err != nil {
		return fmt.Errorf("read migration table failed: %s", err.Error())
	}

	execMigrations := filterMigrations(versions, gMigrations, false)
	// filter migrations by step
	if step > 0 {
		execMigrations = execMigrations[:step]
	}

	// no need to order since `versions` are naturally ordered
	return downMigrations(db, execMigrations)
}

func downMigrations(db *sql.DB, migrations []*Migration) error {
	var err error
	for _, mg := range migrations {
		err = transaction(db, func(tx *sql.Tx) error {
			var e error
			if e = mg.Down(db); e != nil {
				return e
			}

			// delete stmt
			var deleteStmt = fmt.Sprintf("delete from %s where version = ?", tableName)
			_, e = db.Exec(deleteStmt, mg.Version)
			return e
		})

		if err != nil {
			return fmt.Errorf("migration error on version[%s]: %s", mg.Version, err.Error())
		}
	}

	return nil
}
