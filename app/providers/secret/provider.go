package secret

import (
	"crypto/rand"
	"crypto/rsa"
	"crypto/x509"
	"encoding/pem"
	"time"

	"github.com/DemoHn/obsidian-panel/infra"

	"github.com/DemoHn/obsidian-panel/app/drivers/sqlite"
)

// Provider - define interface of secret Provider
type Provider interface {
	NewSecretKey() error
	ToggleSecretKey(id int, isActive bool) error
	GetFirstSecretKey() (*Secret, error)

	// user secrets
	NewUserSecret(accountID int) (string, error)
	GetUserSecret(accountID int) (*UserSecret, error)
	RevokeUserSecret(accountID int) error
}

// Secret - JWT secret key
type Secret struct {
	ID         int
	PublicKey  []byte
	PrivateKey []byte
	Algorithm  string
	Active     bool
}

// UserSecret - get secret of a user
type UserSecret struct {
	ID        int
	AccountID int
	PublicKey []byte
}

// UserSecretHistory - record all actions of users
type UserSecretHistory struct {
	ID         int
	AccountID  int
	Action     string
	HappenedAt time.Time
}

// UserSecretAction - define some enums for user secret actions (login/update/revoke)
type UserSecretAction = string

// iProvider - internal provider
type iProvider struct {
	db *sqlite.Driver
}

const (
	// LOGIN - login
	LOGIN UserSecretAction = "LOGIN"
	// UPDATE - update secret key
	UPDATE UserSecretAction = "UPDATE"
	// REVOKE - revoke the secret key
	REVOKE UserSecretAction = "REVOKE"
)

// helper variables
var log = infra.GetMainLogger()

// New - new provider
func New(db *sqlite.Driver) Provider {
	return &iProvider{
		db: db,
	}
}

// NewSecretKey - when there's no active secret key stored in db
// generate a new secret keypair for its usage
// default algorithm: RS256
func (p iProvider) NewSecretKey() error {
	// gen RSA key pair
	var pub, priv []byte
	var err error

	pub, priv, err = generateRsaKeyPair(1024)
	if err != nil {
		return err
	}

	// store data
	var secret = Secret{
		PublicKey:  pub,
		PrivateKey: priv,
		Algorithm:  "RS256",
		Active:     true,
	}

	if err = insertSecretRecord(p.db, &secret); err != nil {
		return err
	}

	return nil
}

// ToggleSecretKey - toggle enable/disable secretKey
func (p iProvider) ToggleSecretKey(id int, isActive bool) error {
	var err error
	var secret *Secret

	if secret, err = findSecretByID(p.db, id); err != nil {
		return err
	}
	// update data
	_, err = toggleActiveSecret(p.db, secret, isActive)
	return err
}

// GetFirstSecretKey - get first (i.e. most recent generated) secret key pair
func (p iProvider) GetFirstSecretKey() (*Secret, error) {
	return getFirstActiveSecret(p.db)
}

// internal functions
func generateRsaKeyPair(bits int) (publicBytes []byte, privateBytes []byte, err error) {
	// generate RSA key pair
	var privKey *rsa.PrivateKey
	privKey, err = rsa.GenerateKey(rand.Reader, bits)
	if err != nil {
		return
	}

	// get privateKey in []byte
	privateBytes = pem.EncodeToMemory(
		&pem.Block{
			Type:  "RSA PRIVATE KEY",
			Bytes: x509.MarshalPKCS1PrivateKey(privKey),
		},
	)

	// get publicKey in []byte
	var pubASN1 []byte
	pubASN1, err = x509.MarshalPKIXPublicKey(&privKey.PublicKey)
	if err != nil {
		return
	}

	publicBytes = pem.EncodeToMemory(&pem.Block{
		Type:  "RSA PUBLIC KEY",
		Bytes: pubASN1,
	})

	return
}
