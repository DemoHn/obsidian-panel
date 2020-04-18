package account

import (
	"database/sql"
	"fmt"
	"strings"
	"time"
)

const (
	tableName     = "accounts"
	allColumns    = "id, name, credential, permission_level"
	insertColumns = "name, credential, permission_level"
	listColumns   = "id, name, permission_level"
)

// PermLevel - a type defines permission level constants
type PermLevel = string

const (
	// OWNER - panel owner - ownes all permissions in the panel
	// including get the details of machine, etc.
	// We will not use it currently.
	// OWNER   PermLevel = "OWNER"

	// ADMIN - administrator - ownes all permissions except those related
	// to the HOST server itself.
	ADMIN PermLevel = "ADMIN"
	// USER - normal user
	USER PermLevel = "USER"

	// VISITOR - visitor
	// VISITOR PermLevel = "VISITOR"
)

// insertAccountRecord - create Account model
func insertAccountRecord(db *sql.DB, account *Account) error {
	var err error
	var stmt = fmt.Sprintf(`insert into %s (%s, created_at, updated_at) values (?, ?, ?, ?, ?)`, tableName, insertColumns)

	_, err = db.Exec(stmt,
		account.Name,
		account.Credential,
		account.PermLevel,
		time.Now(),
		time.Now(),
	)
	return err
}

// ListAccountsRecord - list account data (without displaying credential, of course)
// notice: limit, offset can be optional
// notice2: offset only affective when limit is not null
func listAccountsRecord(db *sql.DB, filter AccountsFilter) ([]Account, error) {
	var err error
	var rows *sql.Rows

	// if true, prepend "where" statement on the query string
	var whereFlag = false
	var conditionBlocks = []string{}
	var valueBlocks = []interface{}{}

	if filter.NameLike != nil {
		whereFlag = true
		conditionBlocks = append(conditionBlocks, "name like ?")
		valueBlocks = append(valueBlocks, *(filter.NameLike))
	}
	// limit
	if filter.Limit != nil {
		if *(filter.Limit) < 0 {
			return nil, ValidationError("limit < 0")
		}

		conditionBlocks = append(conditionBlocks, "limit ?")
		valueBlocks = append(valueBlocks, *(filter.Limit))
	}
	// offset
	if filter.Limit != nil && filter.Offset != nil {
		if *(filter.Offset) < 0 {
			return nil, ValidationError("offset < 0")
		}

		conditionBlocks = append(conditionBlocks, "offset ?")
		valueBlocks = append(valueBlocks, *(filter.Offset))
	}
	// add "where" statement if necessary
	if whereFlag {
		conditionBlocks = append([]string{"where"}, conditionBlocks...)
	}
	var accounts []Account

	// query statement
	var stmt = fmt.Sprintf("select %s from %s %s", listColumns, tableName, strings.Join(conditionBlocks, " "))
	if rows, err = db.Query(stmt, valueBlocks...); err != nil {
		return nil, SQLExecutionError(err)
	}

	for rows.Next() {
		var newAccount Account
		if err = rows.Scan(&newAccount.ID, &newAccount.Name, &newAccount.PermLevel); err != nil {
			return nil, SQLExecutionError(err)
		}

		accounts = append(accounts, newAccount)
	}

	return accounts, nil
}

// getAccountByName - get account model by name
func getAccountByName(db *sql.DB, name string) (*Account, error) {
	var err error
	var newAccount Account

	var stmt = fmt.Sprintf("select %s from %s where name = ?", allColumns, tableName)
	if err = db.QueryRow(stmt, name).Scan(
		&newAccount.ID,
		&newAccount.Name,
		&newAccount.Credential,
		&newAccount.PermLevel); err != nil {
		if err == sql.ErrNoRows {
			return nil, FindAccountError(name)
		}
		return nil, SQLExecutionError(err)
	}

	return &newAccount, nil
}

// countTotalAccounts - get total accounts
func countTotalAccounts(db *sql.DB) (int, error) {
	var err error
	var stmt = fmt.Sprintf("select count(*) from %s", tableName)

	var count int
	if err = db.QueryRow(stmt).Scan(&count); err != nil {
		return 0, SQLExecutionError(err)
	}
	return count, nil
}

// changePermission - change permission of one account
func changePermission(db *sql.DB, acct *Account, newPerm PermLevel) (*Account, error) {
	var err error
	var stmt = fmt.Sprintf("update %s set permission_level = ? where id = ?", tableName)
	if _, err = db.Exec(stmt, newPerm, acct.ID); err != nil {
		return nil, err
	}

	acct.PermLevel = newPerm
	return acct, nil
}

// changeCredential - update credential
func changeCredential(db *sql.DB, acct *Account, credential []byte) (*Account, error) {
	var err error
	var stmt = fmt.Sprintf("update %s set credential = ? where id = ?", tableName)
	if _, err = db.Exec(stmt, credential, acct.ID); err != nil {
		return nil, err
	}

	acct.Credential = credential
	return acct, nil
}
