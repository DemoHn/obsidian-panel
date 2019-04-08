package util

import (
	"crypto/rsa"
	"crypto/x509"
	"encoding/pem"
	"fmt"
	"time"

	"github.com/DemoHn/obsidian-panel/infra"

	jwt "github.com/dgrijalva/jwt-go"
)

var log = infra.GetMainLogger()

// SignJWT - sign jwt using RS256
func SignJWT(payload map[string]interface{}, secret []byte) (string, error) {
	claims := jwt.MapClaims{}
	for key, val := range payload {
		claims[key] = val
	}

	claims["iss"] = "obsidian-panel"
	claims["exp"] = time.Now().Add(60 * time.Second).Unix()

	token := jwt.NewWithClaims(jwt.SigningMethodRS256, claims)

	privateKey, err := bytesToPrivateKey(secret)
	if err != nil {
		return "", err
	}
	return token.SignedString(privateKey)
}

// VerifyAndDecodeJWT - verify JWT first, if invalid, return error
// after that, decode JWT
func VerifyAndDecodeJWT(token string, secretPublicKey []byte) (map[string]interface{}, error) {
	tok, err := jwt.Parse(token, func(tk *jwt.Token) (interface{}, error) {
		if _, ok := tk.Method.(*jwt.SigningMethodRSA); !ok {
			return nil, fmt.Errorf("invalid singing method")
		}

		return bytesToPublicKey(secretPublicKey)
	})
	if err != nil {
		return nil, err
	}

	claims, ok := tok.Claims.(jwt.MapClaims)
	if ok && tok.Valid {
		return claims, nil
	}

	return nil, addErrorTag("verifyAndDecodeJWT", fmt.Errorf("not ok convert jwt claims to MapClaims"))
}

// bytesToPrivateKey bytes to private key
func bytesToPrivateKey(priv []byte) (*rsa.PrivateKey, error) {
	block, _ := pem.Decode(priv)
	enc := x509.IsEncryptedPEMBlock(block)
	b := block.Bytes
	var err error
	if enc {
		log.Println("is encrypted pem block")
		b, err = x509.DecryptPEMBlock(block, nil)
		if err != nil {
			return nil, addErrorTag("bytesToPrivateKey", err)
		}
	}
	key, err := x509.ParsePKCS1PrivateKey(b)
	if err != nil {
		return nil, addErrorTag("bytesToPrivateKey", err)
	}
	return key, nil
}

// BytesToPublicKey bytes to public key
func bytesToPublicKey(pub []byte) (*rsa.PublicKey, error) {
	block, _ := pem.Decode(pub)
	enc := x509.IsEncryptedPEMBlock(block)
	b := block.Bytes
	var err error
	if enc {
		log.Println("is encrypted pem block")
		b, err = x509.DecryptPEMBlock(block, nil)
		if err != nil {
			return nil, addErrorTag("bytesToPublicKey", err)
		}
	}
	ifc, err := x509.ParsePKIXPublicKey(b)
	if err != nil {
		return nil, addErrorTag("bytesToPublicKey", err)
	}
	key, ok := ifc.(*rsa.PublicKey)
	if !ok {
		return nil, addErrorTag("bytesToPublicKey", fmt.Errorf("not ok"))
	}
	return key, nil
}
