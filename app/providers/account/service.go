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
