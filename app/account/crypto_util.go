package account

import (
	"bytes"
	"crypto/rand"
	"crypto/sha256"
	"crypto/subtle"
	"fmt"
	"strconv"

	"golang.org/x/crypto/pbkdf2"
)

const (
	pinIterations = 250000
	pinSaltLength = 32
	pinKeyLength  = 32
)

// generatePasswordHash - general method to generate and verify a hashKey from string input
// Final hashKey is binary format contains salt, rawKey, iteration & alog info and checksum
//
// HashKey Foramt:
//
// <lenI><lenK><lenS> <[str]iterationLen> <key> <salt>
//
// Notice:
// Due to protocol limitation, <[str]iterationLen>, <key>, <salt>
// length should not be longer than 255
func generatePasswordHash(password string) []byte {
	// generate random bytes
	salt := make([]byte, pinSaltLength)
	_, err := rand.Read(salt)
	// assert generate PIN will work
	if err != nil {
		panic(err)
	}

	key := pbkdf2.Key([]byte(password), salt, pinIterations, pinKeyLength, sha256.New)

	// concat bytes
	info := []byte(fmt.Sprintf("%d", pinIterations))

	header := make([]byte, 3)
	header[0] = byte(len(info))
	header[1] = byte(pinKeyLength)
	header[2] = byte(pinSaltLength)

	finalKey := bytes.Join([][]byte{
		header, info, key, salt,
	}, []byte{})
	return finalKey
}

// verifyPasswordHash - verify if password is correct
func verifyPasswordHash(hashKey []byte, password string) bool {
	// if length not match
	if len(hashKey) < 3 {
		return false
	}

	if int(hashKey[0]+hashKey[1]+hashKey[2]+3) != len(hashKey) {
		return false
	}

	// parse hashKey
	var parseCursor = 3
	var newCursor = parseCursor
	var parseArr = [][]byte{}

	for i := 0; i < 3; i++ {
		newCursor = parseCursor + int(hashKey[i])
		parseArr = append(parseArr, hashKey[parseCursor:newCursor])
		parseCursor = newCursor
	}

	iterations, err := strconv.Atoi(string(parseArr[0]))

	// silent fail
	if err != nil {
		return false
	}
	keyLen := int(hashKey[1])
	key := parseArr[1]
	salt := parseArr[2]
	// generate raw hash using new input password
	newKey := pbkdf2.Key([]byte(password), salt, iterations, keyLen, sha256.New)
	return subtle.ConstantTimeCompare(newKey, key) == 1
}
