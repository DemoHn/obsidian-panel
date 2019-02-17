package account

import (
	"github.com/DemoHn/obsidian-panel/app/drivers/gorm"
	"github.com/DemoHn/obsidian-panel/infra"
)

// Provider - account provider
type Provider interface {
	RegisterAdmin(name string, password string) (*Model, error)
}

type provider struct {
	*infra.Infrastructure
	repo Repository
}

// New - new provider with necessary components
func New(infra *infra.Infrastructure, db *gorm.Driver) Provider {
	return &provider{
		Infrastructure: infra,
		repo: &repository{
			DB:             db,
			Infrastructure: infra,
		},
	}
}
