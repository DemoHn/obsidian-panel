package infra

import (
	"fmt"

	"github.com/fatih/color"
)

// CLILogger -
type CLILogger struct{}

// define func of logger

// PrintInfo - log with white color
func (*CLILogger) PrintInfo(format string, args ...interface{}) {
	c := color.New(color.FgWhite)
	c.Printf(format+"\n", args...)
}

// PrintOK - prefix with colored OK - xxxxyyy
func (*CLILogger) PrintOK(format string, args ...interface{}) {
	g := color.New(color.FgGreen).SprintFunc()

	fmtTpl := fmt.Sprintf("%s - %s\n", g("OK"), format)
	fmt.Printf(fmtTpl, args...)
}

// PrintFail - prefix with colored Fail - xxxyyy
func (*CLILogger) PrintFail(format string, args ...interface{}) {
	r := color.New(color.FgRed).SprintFunc()
	fmtTpl := fmt.Sprintf("%s - %s\n", r("FAIL"), format)
	fmt.Printf(fmtTpl, args...)
}

// PrintError - print error directly to console
// support plain error and *errors.Error type
func (*CLILogger) PrintError(err error) {
	r := color.New(color.FgRed).SprintFunc()
	if cErr, ok := err.(*Error); ok {
		fmt.Printf("%s - (%d) %s: %s\n", r("FAIL"), cErr.ErrorCode, cErr.Name, cErr.Detail)
	} else {
		fmt.Printf("%s - %s\n", r("FAIL"), err.Error())
	}
}

var cliLogger *CLILogger

// LogT - exported var of cliLogger
var LogT *CLILogger

// GetCLILogger - CLI Logger
func GetCLILogger() *CLILogger {
	return cliLogger
}

func init() {
	cliLogger = &CLILogger{}
	LogT = cliLogger
}
