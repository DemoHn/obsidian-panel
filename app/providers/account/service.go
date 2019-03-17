package account

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

	// generate jwt
	return "", nil
}
