package account

import (
	"fmt"

	"github.com/DemoHn/obsidian-panel/app/drivers/gorm"
	"github.com/DemoHn/obsidian-panel/infra"
)

// PermLevel - a type defines permission level constants
type PermLevel = string

const (
	// OWNER - panel owner - ownes all permissions in the panel
	// including get the details of machine, etc.
	// We will not use it currently.
	// OWNER   PermLevel = "OWNER"

	// ADMIN - administrator - ownes all permissions except those related
	// to the HOST server itself.
	ADMIN PermLevel = "ADMIN"
	// USER - normal user
	USER PermLevel = "USER"

	// VISITOR - visitor
	// VISITOR PermLevel = "VISITOR"
)

// Model - account model
type Model struct {
	Name       string    `json:"name"`
	Credential []byte    `json:"-"`
	PermLevel  PermLevel `json:"permLevel"`
}

// Repository - interface of account repository
type Repository interface {
	InsertAccountData(name string, credential []byte, permLevel PermLevel) (*Model, error)
	ListAccountsData(limit *int, offset *int) ([]Model, error)
}

// as internal type, account repository manages all account model related methods
type repository struct {
	*infra.Infrastructure
	DB *gorm.Driver
}

// InsertAccountData - create Model
func (ar *repository) InsertAccountData(name string, credential []byte, permLevel PermLevel) (*Model, error) {
	var err error
	acct := &Model{
		Name:       name,
		Credential: credential,
		PermLevel:  permLevel,
	}

	if err = ar.DB.Create(acct).Error(); err != nil {
		return nil, err
	}

	return acct, nil
}

// ListAccountsData - list account data
// notice: limit, offset can be optional
// notice2: offset only affective when limit is not null
func (ar *repository) ListAccountsData(limit *int, offset *int) ([]Model, error) {
	var err error
	// valiation on limit
	db := ar.DB
	if limit != nil {
		if *limit < 0 {
			// TODO
			return nil, fmt.Errorf("Valdiation Error: limit < 0")
		}

		db = db.Limit(*limit)
	}
	if limit != nil && offset != nil {
		if *offset < 0 {
			// TODO - more readable eror
			return nil, fmt.Errorf("Validation Error: offset < 0")
		}

		db = db.Offset(*offset)
	}

	var accounts []Model
	if err = db.Find(&accounts).Error(); err != nil {
		return nil, err
	}

	return accounts, nil
}
