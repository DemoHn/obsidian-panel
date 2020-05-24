package dbmigrate

import (
	"database/sql"
	"fmt"
)

// Init - init migrations iff. no record in migration_history table
func Init(db *sql.DB) (bool, error) {
	if err := initMigrationTable(db); err != nil {
		return false, err
	}

	// check if migration_history is empty (count = 0)
	var count int
	var countStmt = fmt.Sprintf("select count(*) from %s", tableName)
	if err := db.QueryRow(countStmt).Scan(&count); err != nil {
		return false, err
	}

	if count == 0 {
		if err := upMigrations(db, gMigrations); err != nil {
			return false, err
		}
		return true, nil
	}

	return false, nil
}
