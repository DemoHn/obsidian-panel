package account

import (
	"github.com/DemoHn/obsidian-panel/app/drivers/gorm"
	"github.com/DemoHn/obsidian-panel/infra"
)

// Provider - account provider
type Provider struct {
	*infra.Infrastructure
	accountRepo *accountRepository
}

// New - new provider with necessary components
func New(infra *infra.Infrastructure, db *gorm.Driver) *Provider {
	return &Provider{
		Infrastructure: infra,
		accountRepo: &accountRepository{
			DB:             db,
			Infrastructure: infra,
		},
	}
}

// Name - get the name of account provider
func (p *Provider) Name() string {
	return "account"
}
