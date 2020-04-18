package sqlc

import "database/sql"

// OpenDB -
func OpenDB(dbPath string) (*sql.DB, error) {
	return sql.Open("sqlite3", dbPath)
}
