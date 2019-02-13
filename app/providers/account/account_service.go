package account

// RegisterAdmin - create admin service
func (p *Provider) RegisterAdmin(name string, password string) (*Account, error) {
	// TODO: add password rule check?

	// generate hashKey
	hashKey := generatePasswordHash(password)
	p.Infof("[obs] going to register admin user: %s", name)
	// insert data
	return p.InsertAccountData(name, hashKey, ADMIN)
}
