package logger

import (
	"github.com/sirupsen/logrus"
)

var log *logrus.Logger

// GetLogger - get globally set logger
func GetLogger() *logrus.Logger {
	return log
}

// SetLogger - use external logger to replace default one
func SetLogger(newLogger *logrus.Logger) {
	log = newLogger
}

func init() {
	// load default logger
	log = logrus.New()
}
