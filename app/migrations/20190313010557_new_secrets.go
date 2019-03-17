package migrations

import (
	"github.com/jinzhu/gorm"

	"github.com/DemoHn/obsidian-panel/pkg/dbmigrate"
)

func init() {
	dbmigrate.AddMigration("20190313010557_new_secrets", Up_20190313010557, Down_20190313010557)
}

// Secret - JWT secret key
type Secret struct {
	ID         int    `gorm:"primary_key"`
	PublicKey  []byte `gorm:"type:blob;not null"`
	PrivateKey []byte `gorm:"type:blob;not null"`
	Algorithm  string `gorm:"type:varchar(12);not null"`
	Active     bool   `gorm:"type:boolean"`
}

// Up_20190313010557 - migration up script
func Up_20190313010557(db *gorm.DB) error {
	// Add Up Logic Here!
	var err error
	var secret Secret
	if err = db.CreateTable(&secret).Error; err != nil {
		return err
	}
	return nil
}

// Down_20190313010557 - migration down script
func Down_20190313010557(db *gorm.DB) error {
	// Add Down Logic Here!
	var err error
	if err = db.DropTable("secrets").Error; err != nil {
		return err
	}
	return nil
}
