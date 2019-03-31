package account

import (
	"github.com/DemoHn/obsidian-panel/app/drivers/sqlite"
	"github.com/DemoHn/obsidian-panel/app/providers/secret"

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
}

type iProvider struct {
	db             *sqlite.Driver
	secretProvider secret.Provider
}

// Account - account model
type Account struct {
	ID         int       `json:"id"`
	Name       string    `json:"name"`
	Credential []byte    `json:"-"`
	PermLevel  PermLevel `json:"permLevel"`
}

// New - new provider with necessary components
func New(db *sqlite.Driver, secretProvider secret.Provider) Provider {
	return &iProvider{
		db:             db,
		secretProvider: secretProvider,
	}
}

// RegisterAdmin - create admin service
func (p iProvider) RegisterAdmin(name string, password string) error {
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

func (p iProvider) Login(name string, password string) (string, error) {
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

	return signJWT(map[string]interface{}{
		"accountId": acct.ID,
		"name":      acct.Name,
	}, secret.PrivateKey)
}
