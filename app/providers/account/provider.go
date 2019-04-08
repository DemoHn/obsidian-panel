package account

import (
	"github.com/DemoHn/obsidian-panel/app/drivers"
	"github.com/DemoHn/obsidian-panel/app/drivers/echo"
	"github.com/DemoHn/obsidian-panel/app/drivers/sqlite"
	"github.com/DemoHn/obsidian-panel/app/providers/secret"
	"github.com/DemoHn/obsidian-panel/util"

	// init infra configs
	"github.com/DemoHn/obsidian-panel/infra"
)

// infra variables
var log = infra.GetMainLogger()
var config = infra.GetConfig()

// Provider - account provider
type Provider interface {
	RegisterAdmin(name string, password string) error
	Login(name string, password string) (string, error)
	CountAccounts() (int, error)
	ListAccountsByFilter(filter AccountsFilter) ([]Account, error)
}

type iProvider struct {
	db             *sqlite.Driver
	echo           *echo.Driver
	secretProvider secret.Provider
}

// AccountsFilter - define filter properties for listing accounts
type AccountsFilter struct {
	nameLike *string
	limit    *int
	offset   *int
}

// Account - account model
type Account struct {
	ID         int       `json:"id"`
	Name       string    `json:"name"`
	Credential []byte    `json:"-"`
	PermLevel  PermLevel `json:"permLevel"`
}

// New - new provider with necessary components
func New(drv *drivers.Drivers, secretProvider secret.Provider) Provider {
	p := &iProvider{
		db:             drv.Sqlite,
		echo:           drv.Echo,
		secretProvider: secretProvider,
	}

	p.registerAPIs()
	return p
}

// RegisterAdmin - create admin service
func (p iProvider) RegisterAdmin(name string, password string) error {
	return p.registerAdmin(name, password)
}

func (p iProvider) ListAccountsByFilter(filter AccountsFilter) ([]Account, error) {
	return listAccountsRecord(p.db, filter)
}

func (p iProvider) CountAccounts() (int, error) {
	return countTotalAccounts(p.db)
}

// Login - get a new signed JWT to login the obsidian-panel
func (p iProvider) Login(name string, password string) (string, error) {
	return p.login(name, password)
}

// internal functions
func (p iProvider) registerAdmin(name string, password string) error {
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
	return insertAccountRecord(p.db, &acct)
}

func (p iProvider) login(name string, password string) (string, error) {
	var err error
	var acct *Account
	// find account
	if acct, err = getAccountByName(p.db, name); err != nil {
		return "", err
	}

	// compare password
	if !verifyPasswordHash(acct.Credential, password) {
		return "", IncorrectPasswordError()
	}

	// get secret key
	secret, err := p.secretProvider.GetFirstSecretKey()
	if err != nil {
		return "", err
	}

	return util.SignJWT(map[string]interface{}{
		"accountId":  acct.ID,
		"name":       acct.Name,
		"permission": acct.PermLevel,
	}, secret.PrivateKey)
}
