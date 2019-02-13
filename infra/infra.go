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
	var cfg *Config
	if cfg, err = config.Init(configFile); err != nil {
		return nil, err
	}

	return &Infrastructure{
		Config:    cfg,
		Logger:    logger.Init(debugMode),
		debugMode: debugMode,
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

// DebugMode - check if on debugMode
func (inf *Infrastructure) DebugMode() bool {
	return inf.debugMode
}

// NewError - return an new error with more intuitive format
func NewError(name string, statusCode int, errorCode int, detail string, info interface{}) *errors.Error {
	// TODO: refactor it!
	return &errors.Error{
		Name:       name,
		StatusCode: statusCode,
		ErrorCode:  errorCode,
		Info:       info,
		Detail:     detail,
	}
}

// NewErrorClass - create new set of errors
func NewErrorClass(classCode int) *errors.ErrorClass {
	return &errors.ErrorClass{
		ClassCode: classCode,
	}
}
