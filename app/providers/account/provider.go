package account

import (
	"github.com/DemoHn/obsidian-panel/app/drivers/gorm"
	"github.com/DemoHn/obsidian-panel/app/providers/secret"

	// init infra configs
	"github.com/DemoHn/obsidian-panel/infra"
)

// infra variables
var log = infra.GetMainLogger()
var config = infra.GetConfig()

// Provider - account provider
type Provider interface {
	RegisterAdmin(name string, password string) (*Model, error)
	Login(name string, password string) (string, error)
}

type provider struct {
	repo           Repository
	secretProvider secret.Provider
}

// New - new provider with necessary components
func New(db *gorm.Driver, secretProvider secret.Provider) Provider {
	return &provider{
		repo:           &repository{db},
		secretProvider: secretProvider,
	}
}

// RegisterAdmin - create admin service
func (p provider) RegisterAdmin(name string, password string) (*Model, error) {
	// TODO: add password rule check?

	// generate hashKey
	hashKey := generatePasswordHash(password)
	log.Debugf("[obs] going to register admin user: %s", name)
	// insert data
	return p.repo.InsertAccountData(name, hashKey, ADMIN)
}

func (p provider) Login(name string, password string) (string, error) {
	var err error
	var acct *Model
	// find account
	if acct, err = p.repo.GetAccountByName(name); err != nil {
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
