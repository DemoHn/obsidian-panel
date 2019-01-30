package logger

import (
	"github.com/sirupsen/logrus"
)

// Logger - alias of logrus.Logger
type Logger = logrus.Logger

// Init - init an instance
func Init(debugMode bool) *Logger {
	// if not inited
	logger := logrus.New()

	logger.SetFormatter(&logrus.TextFormatter{
		FullTimestamp:          true,
		DisableLevelTruncation: true,
		// <date>/<month>/<year> <Hour>:<minute>:<second>.<ms> <tz>
		TimestampFormat: "02/01/2006 15:04:05.999 MST",
	})
	if debugMode {
		logger.SetLevel(logrus.DebugLevel)
	} else {
		logger.SetLevel(logrus.InfoLevel)
	}
	return logger
}
