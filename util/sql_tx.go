package util

import "database/sql"

// TransactionFunc - transaction function
type TransactionFunc func(tx *sql.Tx) error

// TransactionDB - a wrapper for creating a transaction
func TransactionDB(db *sql.DB, fn TransactionFunc) error {
	tx, err := db.Begin()
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
