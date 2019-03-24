package account

import (
	"github.com/DemoHn/obsidian-panel/app/drivers/gorm"
	"github.com/DemoHn/obsidian-panel/app/providers/secret"

	// init infra configs
	"github.com/DemoHn/obsidian-panel/infra"
)

// infra variables
var log = infra.GetMainLogger()
var config = infra.GetConfig()

// Provider - account provider
type Provider interface {
	RegisterAdmin(name string, password string) (*Model, error)
	Login(name string, password string) (string, error)
}

type provider struct {
	repo           Repository
	secretProvider secret.Provider
}

// New - new provider with necessary components
func New(db *gorm.Driver, secretProvider secret.Provider) Provider {
	return &provider{
		repo:           &repository{db},
		secretProvider: secretProvider,
	}
}
