package infra

import (
	"github.com/DemoHn/obsidian-panel/infra/config"
	"github.com/DemoHn/obsidian-panel/infra/errors"
	"github.com/DemoHn/obsidian-panel/infra/logger"
)

// Config -
type Config = config.Config

// Logger -
type Logger = logger.Logger

// Infrastructure defines the basic components that nearly every providers & drivers
// will use. (e.g. logger)
type Infrastructure struct {
	*Config
	*Logger
	debugMode bool
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

// NewError - return an new error with more intuitive format
func (inf *Infrastructure) NewError(name string, err error) *errors.Error {
	// TODO: refactor it!
	return &errors.Error{
		Name:       name,
		StatusCode: 400,
		ErrorCode:  20000,
		Detail:     err.Error(),
		DebugMode:  inf.debugMode,
	}
}
