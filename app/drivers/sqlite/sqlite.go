package sqlite

import "database/sql"

// Driver - sqlite driver wraps sqlite
type Driver struct {
	DB *sql.DB
}
