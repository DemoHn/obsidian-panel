package app

import "github.com/DemoHn/obsidian-panel/app/drivers/gorm"

// Secret - JWT secret key
type Secret struct {
	ID         int
	PublicKey  []byte
	PrivateKey []byte
	Algorithm  string
	Active     bool
}

// InitSecretKey - when there's no active secret key stored in db
// generate a new secret keypair for its usage
func InitSecretKey(db *gorm.Driver) {

}
