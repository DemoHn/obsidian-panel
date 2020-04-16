package secret

import (
	"database/sql"
	"fmt"

	"time"

	"github.com/DemoHn/obsidian-panel/util"
)

const (
	usTableName   = "user_secrets"
	usAllColumns  = "id, account_id"
	ushTableName  = "user_secrets_history"
	acctTableName = "accounts"
)

// insertUserPublicKey - store the **PUBLIC** key of the recently
// generated key pair.
// BTW, the **PRIVATE** key will be used to genearte a jwt string in the
// following time without saving to persist db
func insertUserPublicKey(db *sql.DB, accountID int, publicKey []byte) (*UserSecret, error) {
	var err error

	var insertStmt = fmt.Sprintf("insert into %s (account_id, public_key) values (?, ?)", usTableName)
	var insertHistoryStmt = fmt.Sprintf("insert into %s (account_id, action, happened_at) values (?, ?, ?)", ushTableName)

	err = util.TransactionDB(db, func(tx *sql.Tx) error {
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
func findUserSecret(db *sql.DB, accountID int) (bool, *UserSecret, error) {
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

func updateUserPublicKey(db *sql.DB, accountID int, publicKey []byte) (*UserSecret, error) {
	var err error
	// ensure accountID exists, since we don't use foreign keys

	var insertStmt = fmt.Sprintf("update %s set public_key = ? where account_id = ?", usTableName)
	var insertHistoryStmt = fmt.Sprintf("insert into %s (account_id, action, happened_at) values (?, ?, ?)", ushTableName)

	err = util.TransactionDB(db, func(tx *sql.Tx) error {
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

func revokeUserPublicKey(db *sql.DB, accountID int) error {
	var err error

	var revokeStmt = fmt.Sprintf("delete from %s where account_id = ?", usTableName)
	var insertHistoryStmt = fmt.Sprintf("insert into %s (account_id, action, happened_at) values (?, ?, ?)", ushTableName)

	err = util.TransactionDB(db, func(tx *sql.Tx) error {
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

func verifyAccountID(db *sql.DB, accountID int) error {
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
