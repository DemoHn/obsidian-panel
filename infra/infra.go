package infra

import (
	"github.com/DemoHn/obsidian-panel/infra/config"
	"github.com/DemoHn/obsidian-panel/infra/logger"
)

// Infrastructure defines the basic components that nearly every providers & drivers
// will use. (e.g. logger)

type Config = config.Config
type Logger = logger.Logger
type Infrastructure struct {
	*Config
	*Logger
}

// New - New Infrastructure
func New(configFile string, debugMode bool) (*Infrastructure, error) {
	var err error
	var cfg *config.Config
	if cfg, err = config.Init(configFile); err != nil {
		return nil, err
	}

	return &Infrastructure{
		Config: cfg,
		Logger: logger.Init(debugMode),
	}, nil
}

// GetConfig - get config component
func (inf *Infrastructure) GetConfig() *Config {
	return inf.Config
}

// GetLogger - get logger component
func (inf *Infrastructure) GetLogger() *Logger {
	return inf.Logger
}
