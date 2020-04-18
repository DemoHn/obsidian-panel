package account

import (
	"database/sql"

	"github.com/DemoHn/obsidian-panel/app/secret"
	"github.com/DemoHn/obsidian-panel/infra"
	"github.com/DemoHn/obsidian-panel/util"
)

// infra variables
var log = infra.Log

// AccountsFilter - define filter properties for listing accounts
type AccountsFilter struct {
	NameLike *string
	Limit    *int
	Offset   *int
}

// Account - account model
type Account struct {
	ID         int       `json:"id"`
	Name       string    `json:"name"`
	Credential []byte    `json:"-"`
	PermLevel  PermLevel `json:"permLevel"`
}

// RegisterAdmin - create admin service
func RegisterAdmin(db *sql.DB, name string, password string) error {
	return registerAdmin(db, name, password)
}

// RegisterAdminNS - register admin if NOT EXISTS
func RegisterAdminNS(db *sql.DB, name string, password string) error {
	exists, err := accountExists(db, name)
	if err != nil {
		return err
	}
	// only insert admin if not exists
	if !exists {
		return registerAdmin(db, name, password)
	}
	return nil
}

// ListAccountsByFilter -
func ListAccountsByFilter(db *sql.DB, filter AccountsFilter) ([]Account, error) {
	return listAccountsRecord(db, filter)
}

// CountAccounts - count the number of total accounts
func CountAccounts(db *sql.DB) (int, error) {
	return countTotalAccounts(db)
}

// ResetPassword -
func ResetPassword(db *sql.DB, name string, newPassword string) (string, error) {
	var err error
	var acct *Account
	// find account
	if acct, err = getAccountByName(db, name); err != nil {
		return "", err
	}

	// get secret key
	privateKey, err := secret.RotateUserSecret(db, acct.ID)
	if err != nil {
		return "", err
	}
	// generate hashKey with new Password
	hashKey := generatePasswordHash(newPassword)
	// update credential
	if acct, err = changeCredential(db, acct, hashKey); err != nil {
		return "", err
	}

	return util.SignJWT(map[string]interface{}{
		"accountId":  acct.ID,
		"name":       acct.Name,
		"permission": acct.PermLevel,
	}, privateKey)
}

// ChangePermission -
func ChangePermission(db *sql.DB, name string, newPerm PermLevel) (*Account, error) {
	var err error
	var acct *Account
	// find account
	if acct, err = getAccountByName(db, name); err != nil {
		return nil, err
	}

	return changePermission(db, acct, newPerm)
}

// Login - get a new signed JWT to login the obsidian-panel
func Login(db *sql.DB, name string, password string) (string, error) {
	return login(db, name, password)
}

// internal functions
func registerAdmin(db *sql.DB, name string, password string) error {
	// TODO: add password rule check?

	// generate hashKey
	hashKey := generatePasswordHash(password)
	log.Debugf("[obs] going to register admin user: %s", name)
	// insert data

	acct := Account{
		Name:       name,
		Credential: hashKey,
		PermLevel:  ADMIN,
	}
	return insertAccountRecord(db, &acct)
}

func login(db *sql.DB, name string, password string) (string, error) {
	var err error
	var acct *Account
	// find account
	if acct, err = getAccountByName(db, name); err != nil {
		return "", err
	}

	// compare password
	if !verifyPasswordHash(acct.Credential, password) {
		return "", IncorrectPasswordError()
	}

	// get secret key
	privateKey, err := secret.RotateUserSecret(db, acct.ID)
	if err != nil {
		return "", err
	}

	return util.SignJWT(map[string]interface{}{
		"accountId":  acct.ID,
		"name":       acct.Name,
		"permission": acct.PermLevel,
	}, privateKey)
}
