package account

import "fmt"

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

// Account - account model
type Account struct {
	Name       string    `json:"name"`
	Credential []byte    `json:"-"`
	PermLevel  PermLevel `json:"permLevel"`
}

// InsertAccountData - create Account in model level
func (p *Provider) InsertAccountData(name string, credential []byte, permLevel PermLevel) (*Account, error) {
	var err error
	acct := &Account{
		Name:       name,
		Credential: credential,
		PermLevel:  permLevel,
	}

	if err = p.DB.Create(acct).Error(); err != nil {
		return nil, err
	}

	return acct, nil
}

// ListAccountsData - list account data
// notice: limit, offset can be optional
// notice2: offset only affective when limit is not null
func (p *Provider) ListAccountsData(limit *int, offset *int) ([]Account, error) {
	var err error
	// valiation on limit
	db := p.DB
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

	var accounts []Account
	if err = db.Find(&accounts).Error(); err != nil {
		return nil, err
	}

	return accounts, nil
}
