package processmanager

import (
	"github.com/DemoHn/obsidian-panel/pkg/cfgparser"
)

// Provider - process manager (apm)
type Provider interface {
}

type provider struct {
	DebugMode   bool
	localConfig *cfgparser.Config
}

// New - new provider
func New(debugMode bool) Provider {
	localConfig := cfgparser.New("yaml")
	// loads default config
	localConfig.LoadDefault(map[string]interface{}{
		"global.cfgfile": "a",
	})

	return &provider{
		DebugMode:   debugMode,
		localConfig: localConfig,
	}
}

// ReloadConfig - reload config from main configlet
func (p *provider) ReloadConfig() error {
	//var err error
	return nil
}

// StartDaemon - start daemon
func (p *provider) StartDaemon() error {
	return nil
}
