package secret

import (
	"crypto/rand"
	"crypto/rsa"
	"crypto/x509"
	"encoding/pem"
	"fmt"

	"github.com/DemoHn/obsidian-panel/infra"

	"github.com/DemoHn/obsidian-panel/app/drivers/gorm"
)

// Provider - define interface of secret Provider
type Provider interface {
	NewSecretKey() error
	ToggleSecretKey(id int, isActive bool) error
	GetFirstSecretKey() (*Secret, error)
}

// Secret - JWT secret key
type Secret struct {
	ID         int
	PublicKey  []byte
	PrivateKey []byte
	Algorithm  string
	Active     bool
}

// actual provider definition
type provider struct {
	db *gorm.Driver
}

// helper variables
var log = infra.GetMainLogger()

// New - new provider
func New(db *gorm.Driver) Provider {
	return &provider{
		db: db,
	}
}

// NewSecretKey - when there's no active secret key stored in db
// generate a new secret keypair for its usage
// default algorithm: RS256
func (p provider) NewSecretKey() error {
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

	if err = p.db.Create(&secret).Error; err != nil {
		return err
	}

	return nil
}

// ToggleSecretKey - toggle enable/disable secretKey
func (p provider) ToggleSecretKey(id int, isActive bool) error {
	var err error

	var secrets []Secret
	if err = p.db.Where("id = ?", id).Find(&secrets).Error; err != nil {
		return err
	}
	// nothing found
	if len(secrets) == 0 {
		return fmt.Errorf("secret:%d not found", id)
	}

	// update data
	if err = p.db.Model(&secrets[0]).Update("active = ?", isActive).Error; err != nil {
		return err
	}

	return nil
}

// GetFirstSecretKey - get first (i.e. most recent generated) secret key pair
func (p provider) GetFirstSecretKey() (*Secret, error) {
	var err error

	var secret Secret
	if err = p.db.Order("createdAt desc").First(&secret).Error; err != nil {
		return nil, err
	}
	return &secret, nil
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