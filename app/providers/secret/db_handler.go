package secret

import (
	"database/sql"
	"fmt"

	"time"

	"github.com/jinzhu/copier"

	"github.com/DemoHn/obsidian-panel/app/drivers/sqlite"
)

const (
	tableName  = "secrets"
	allColumns = "public_key, private_key, algorithm, active"
)

// insertSecretRecord - insert Secret model to database
func insertSecretRecord(db *sqlite.Driver, secret *Secret) error {
	var err error
	var stmt = fmt.Sprintf(`insert into %s (%s, created_at, updated_at) values (?, ?, ?, ?, ?, ?)`, tableName, allColumns)

	// insert data
	_, err = db.Exec(stmt,
		secret.PublicKey,
		secret.PrivateKey,
		secret.Algorithm,
		secret.Active,
		// created_at, updated_at
		time.Now(),
		time.Now(),
	)
	return err
}

// findSecretByID - find secret by Id
func findSecretByID(db *sqlite.Driver, id int) (*Secret, error) {
	var stmt = fmt.Sprintf(`select %s from %s where id = ?`, allColumns, tableName)

	var err error
	var row *sql.Row
	// find one record or not
	var publicKey, privateKey []byte
	var algorithm string
	var active bool

	row = db.QueryRow(stmt, id)
	if err = row.Scan(&publicKey, &privateKey, &algorithm, &active); err != nil {
		return nil, err
	}

	return &Secret{
		PublicKey:  publicKey,
		PrivateKey: privateKey,
		Algorithm:  algorithm,
		Active:     active,
	}, nil
}

// toggleActiveSecret - enable/disable one secret key
func toggleActiveSecret(db *sqlite.Driver, secret *Secret, active bool) (*Secret, error) {
	var stmt = fmt.Sprintf("update %s set active = ?, updated_at = ? where id = ?", tableName)

	var err error
	if _, err = db.Exec(stmt, active, time.Now(), secret.ID); err != nil {
		return nil, err
	}
	// duplicate new secret model
	var newSecret Secret
	copier.Copy(&newSecret, secret)
	newSecret.Active = active

	return &newSecret, nil
}

// getFirstActiveSecret - get first available secret key
func getFirstActiveSecret(db *sqlite.Driver) (*Secret, error) {
	var stmt = fmt.Sprintf(`select %s from %s 
	where active = true 
	order by created_at desc
	limit 1
	`, allColumns, tableName)

	var err error
	var row *sql.Row
	var publicKey, privateKey []byte
	var algorithm string
	var active bool

	row = db.QueryRow(stmt)
	if err = row.Scan(&publicKey, &privateKey, &algorithm, &active); err != nil {
		return nil, err
	}

	return &Secret{
		PublicKey:  publicKey,
		PrivateKey: privateKey,
		Algorithm:  algorithm,
		Active:     active,
	}, nil
}
