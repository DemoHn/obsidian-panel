package account

import (
	"crypto/rsa"
	"crypto/x509"
	"encoding/pem"

	jwt "github.com/dgrijalva/jwt-go"
)

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
	// generate jwt
	token := jwt.NewWithClaims(jwt.SigningMethodRS256, jwt.MapClaims{
		"accountId": acct.ID,
		"name":      acct.Name,
	})

	// Sign and get the complete encoded token as a string using the secret
	tokenString, err := token.SignedString(bytesToPrivateKey(secret.PrivateKey))
	if err != nil {
		return "", err
	}
	return tokenString, nil
}

// internal functions
// bytesToPrivateKey bytes to private key
func bytesToPrivateKey(priv []byte) *rsa.PrivateKey {
	block, _ := pem.Decode(priv)
	enc := x509.IsEncryptedPEMBlock(block)
	b := block.Bytes
	var err error
	if enc {
		log.Println("is encrypted pem block")
		b, err = x509.DecryptPEMBlock(block, nil)
		if err != nil {
			log.Error(err)
		}
	}
	key, err := x509.ParsePKCS1PrivateKey(b)
	if err != nil {
		log.Error(err)
	}
	return key
}
