package procmanager

import (
	"time"

	apmDaemon "github.com/DemoHn/obsidian-panel/pkg/apm/daemon"
	"github.com/DemoHn/obsidian-panel/pkg/cfgparser"
)

// Provider - process manager (apm)
type Provider interface {
	ReloadConfig() error
	StartDaemon(foreground bool) error
	PingDaemon() error
}

type provider struct {
	debugMode   bool
	localConfig *cfgparser.Config
}

// New - new provider
func New(debugMode bool) Provider {
	localConfig := cfgparser.New("yaml")
	// loads default config
	localConfig.LoadDefault(map[string]interface{}{
		"global.dir":      "./.apm",
		"global.pidFile":  "$(global.dir)/apm.pid",
		"global.logFile":  "$(global.dir)/apm.log",
		"global.sockFile": "$(global.dir)/apm.sock",
	})

	return &provider{
		debugMode:   debugMode,
		localConfig: localConfig,
	}
}

// ReloadConfig - reload config from main configlet
func (p *provider) ReloadConfig() error {
	//var err error
	return nil
}

// StartDaemon - start daemon
func (p *provider) StartDaemon(foreground bool) error {
	if foreground {
		return apmDaemon.StartForeground(p.localConfig, p.debugMode)
	}
	return apmDaemon.Start(p.localConfig, p.debugMode)
}

// PingDaemon - ping daemon to ensure daemon has connected
// TODO: Config ping time
func (p *provider) PingDaemon() error {
	return apmDaemon.PingTimeout(p.localConfig, time.Second*5, time.Second*30)
}
