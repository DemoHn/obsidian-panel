package util

import (
	"crypto/rsa"
	"crypto/x509"
	"encoding/pem"
	"time"

	"github.com/DemoHn/obsidian-panel/infra"

	jwt "github.com/dgrijalva/jwt-go"
)

var log = infra.GetMainLogger()

// SignJWT -
func SignJWT(payload map[string]interface{}, secret []byte) (string, error) {
	claims := jwt.MapClaims{}
	for key, val := range payload {
		claims[key] = val
	}

	claims["iss"] = "obsidian-panel"
	claims["exp"] = time.Now().Add(60 * time.Second).Unix()

	token := jwt.NewWithClaims(jwt.SigningMethodRS256, claims)
	return token.SignedString(bytesToPrivateKey(secret))
}

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
