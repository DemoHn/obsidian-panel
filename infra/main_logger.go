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

// Log - main Log instance
var Log *logrus.Logger

func init() {
	logger = logrus.New()
	// set defaults
	logger.SetFormatter(&logrus.TextFormatter{
		FullTimestamp:          true,
		DisableLevelTruncation: true,
		// <year>-<month>-<date> <Hour>:<minute>:<second>.<ms> <tz>
		TimestampFormat: "2006-01-02 15:04:05.999 MST",
	})
	// set default logger level
	logger.SetLevel(logrus.InfoLevel)
	Log = logger
}
