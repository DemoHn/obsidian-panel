package infra

import "github.com/sirupsen/logrus"

var logger *logrus.Logger

// GetMainLogger - getter
func GetMainLogger() *logrus.Logger {
	return logger
}

// SetMainLoggerLevel - setLevel() of main logger
func SetMainLoggerLevel(debugMode bool) {
	if debugMode {
		logger.SetLevel(logrus.DebugLevel)
	} else {
		logger.SetLevel(logrus.InfoLevel)
	}
}

// SetMainLogger - logger setter
func SetMainLogger(newLogger *logrus.Logger) {
	logger = newLogger
}

func init() {
	logger = logrus.New()
	// set defaults
	logger.SetFormatter(&logrus.TextFormatter{
		FullTimestamp:          true,
		DisableLevelTruncation: true,
		// <date>/<month>/<year> <Hour>:<minute>:<second>.<ms> <tz>
		TimestampFormat: "02/01/2006 15:04:05.999 MST",
	})
	// set default logger level
	logger.SetLevel(logrus.InfoLevel)
}
