package account

import (
	"github.com/DemoHn/obsidian-panel/app/drivers/gorm"
	// init infra configs
	"github.com/DemoHn/obsidian-panel/infra"
)

// infra variables
var log = infra.GetMainLogger()
var config = infra.GetConfig()

// Provider - account provider
type Provider interface {
	RegisterAdmin(name string, password string) (*Model, error)
}

type provider struct {
	repo Repository
}

// New - new provider with necessary components
func New(db *gorm.Driver) Provider {
	return &provider{
		repo: &repository{db},
	}
}
