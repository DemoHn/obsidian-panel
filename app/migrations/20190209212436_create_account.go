package migrations

import (
	"github.com/jinzhu/gorm"

	"github.com/DemoHn/obsidian-panel/pkg/dbmigrate"
)

func init() {
	dbmigrate.AddMigration("20190209212436_create_account", Up_20190209212436, Down_20190209212436)
}

// Account - account definition
type Account struct {
	ID int `gorm:"primary_key" json:"id"`
	// Name - account name
	Name string `gorm:"type:text;not null" json:"name"`
	// Credential - hashed password
	Credential []byte `gorm:"type:blob;not null" json:"-"`
	// PermLevel - permission level
	PermLevel string `gorm:"type:varchar(10);not null"`
}

// Up_20190209212436 - migration up script
func Up_20190209212436(db *gorm.DB) error {
	// Add Up Logic Here!
	var err error
	var account Account
	if err = db.CreateTable(&account).Error; err != nil {
		return err
	}
	return nil
}

// Down_20190209212436 - migration down script
func Down_20190209212436(db *gorm.DB) error {
	// Add Down Logic Here!
	var err error
	if err = db.DropTable("accounts").Error; err != nil {
		return err
	}
	return nil
}
