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

	usTableName   = "user_secrets"
	usAllColumns  = "id, account_id"
	ushTableName  = "user_secrets_history"
	acctTableName = "accounts"
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

// insertUserPublicKey - store the **PUBLIC** key of the recently
// generated key pair.
// BTW, the **PRIVATE** key will be used to genearte a jwt string in the
// following time without saving to persist db
func insertUserPublicKey(db *sqlite.Driver, accountID int, publicKey []byte) (*UserSecret, error) {
	var err error

	var insertStmt = fmt.Sprintf("insert into %s (account_id, public_key) values (?, ?)", usTableName)
	var insertHistoryStmt = fmt.Sprintf("insert into %s (account_id, action, happened_at) values (?, ?, ?)", ushTableName)

	err = db.Transaction(func(tx *sql.Tx) error {
		var e error
		if _, e = tx.Exec(insertStmt, accountID, publicKey); e != nil {
			return e
		}
		if _, e = tx.Exec(insertHistoryStmt, accountID, LOGIN, time.Now()); e != nil {
			return e
		}
		return nil
	})
	if err != nil {
		return nil, err
	}

	return &UserSecret{
		AccountID: accountID,
	}, nil
}

// findUserPublicKey - find user public key
// return `true, <item>, nil` if the according userSecret has found
// return `false, nil, nil` if the according userSecret has not found
// return `xx, xx, <error>` if the error has been happened
func findUserSecret(db *sqlite.Driver, accountID int) (bool, *UserSecret, error) {
	var err error
	var uSecret = UserSecret{}
	var findStmt = fmt.Sprintf("select %s from %s where account_id = ?", usAllColumns, usTableName)

	if err = db.QueryRow(findStmt, accountID).Scan(&uSecret.ID, &uSecret.AccountID); err != nil {
		if err == sql.ErrNoRows {
			return false, nil, nil
		}
		return false, nil, err
	}

	return true, &uSecret, nil
}

func updateUserPublicKey(db *sqlite.Driver, accountID int, publicKey []byte) (*UserSecret, error) {
	var err error
	// ensure accountID exists, since we don't use foreign keys

	var insertStmt = fmt.Sprintf("update %s set public_key = ? where account_id = ?", usTableName)
	var insertHistoryStmt = fmt.Sprintf("insert into %s (account_id, action, happened_at) values (?, ?, ?)", ushTableName)

	err = db.Transaction(func(tx *sql.Tx) error {
		var e error
		if _, e = tx.Exec(insertStmt, publicKey, accountID); e != nil {
			return e
		}
		if _, e = tx.Exec(insertHistoryStmt, accountID, UPDATE, time.Now()); e != nil {
			return e
		}
		return nil
	})
	if err != nil {
		return nil, err
	}

	return &UserSecret{
		AccountID: accountID,
	}, nil
}

func revokeUserPublicKey(db *sqlite.Driver, accountID int) error {
	var err error

	var revokeStmt = fmt.Sprintf("delete from %s where account_id = ?", usTableName)
	var insertHistoryStmt = fmt.Sprintf("insert into %s (account_id, action, happened_at) values (?, ?, ?)", ushTableName)

	err = db.Transaction(func(tx *sql.Tx) error {
		var e error
		if _, e = tx.Exec(revokeStmt, accountID); e != nil {
			return e
		}
		if _, e = tx.Exec(insertHistoryStmt, accountID, REVOKE, time.Now()); e != nil {
			return e
		}
		return nil
	})
	if err != nil {
		return err
	}

	return nil
}

func verifyAccountID(db *sqlite.Driver, accountID int) error {
	var err error
	var stmt = fmt.Sprintf("select id from %s where id = ?", acctTableName)
	var acctID int

	if err = db.QueryRow(stmt, accountID).Scan(&acctID); err != nil {
		if err == sql.ErrNoRows {
			return AccountNotFoundError(accountID)
		}
		return err
	}

	return nil
}
