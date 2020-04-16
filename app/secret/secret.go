package secret

import (
	"crypto/rand"
	"crypto/rsa"
	"crypto/x509"
	"database/sql"
	"encoding/pem"
	"time"

	"github.com/DemoHn/obsidian-panel/infra"
)

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

const (
	// LOGIN - login
	LOGIN UserSecretAction = "LOGIN"
	// UPDATE - update secret key
	UPDATE UserSecretAction = "UPDATE"
	// REVOKE - revoke the secret key
	REVOKE UserSecretAction = "REVOKE"
)

// helper variables
var log = infra.Log

// NewUserSecret - create user secret for login
func NewUserSecret(db *sql.DB, accountID int) ([]byte, error) {
	var err error
	// verify accountID first
	if err = verifyAccountID(db, accountID); err != nil {
		return nil, err
	}
	// new rsa key pair
	publicBytes, privateBytes, err := generateRsaKeyPair(512)
	if err != nil {
		return nil, err
	}

	if _, err = insertUserPublicKey(db, accountID, publicBytes); err != nil {
		return nil, err
	}

	return privateBytes, nil
}

// GetUserSecret - get user secret
func GetUserSecret(db *sql.DB, accountID int) (*UserSecret, error) {
	var err error
	// verify accountID first
	if err = verifyAccountID(db, accountID); err != nil {
		return nil, err
	}
	// get user secret
	find, secret, err := findUserSecret(db, accountID)
	if err != nil {
		return nil, err
	}
	if find == false {
		return nil, UserSecretNotFoundError(accountID)
	}

	return secret, nil
}

// RotateUserSecret - insert or update user secret & generate the final jwt
func RotateUserSecret(db *sql.DB, accountID int) ([]byte, error) {
	var err error
	// verify accountID first
	if err = verifyAccountID(db, accountID); err != nil {
		return nil, err
	}
	// new rsa key pair
	publicBytes, privateBytes, err := generateRsaKeyPair(512)
	if err != nil {
		return nil, err
	}

	// get user secret to determine insert or update
	find, _, err := findUserSecret(db, accountID)
	if err != nil {
		return nil, err
	}
	if find == false {
		if _, err = insertUserPublicKey(db, accountID, publicBytes); err != nil {
			return nil, err
		}
	} else {
		if _, err = updateUserPublicKey(db, accountID, publicBytes); err != nil {
			return nil, err
		}
	}
	return privateBytes, nil
}

// RevokeUserSecret - revoke user secret
func RevokeUserSecret(db *sql.DB, accountID int) error {
	var err error
	// verify accountID first
	if err = verifyAccountID(db, accountID); err != nil {
		return err
	}
	// get user secret
	find, _, err := findUserSecret(db, accountID)
	if err != nil {
		return err
	}
	if find == false {
		// do nothing
		return nil
	}

	return revokeUserPublicKey(db, accountID)
}

// internal helpers
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
