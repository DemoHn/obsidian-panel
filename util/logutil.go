package util

// logUtil is used for logging in CLI interface
import (
	"fmt"

	"github.com/DemoHn/obsidian-panel/infra/errors"
	"github.com/fatih/color"
)

// LogInfo - log with white color
func LogInfo(format string, args ...interface{}) {
	c := color.New(color.FgWhite)
	c.Printf(format+"\n", args...)
}

// LogOK - prefix with colored OK - xxxxyyy
func LogOK(format string, args ...interface{}) {
	g := color.New(color.FgGreen).SprintFunc()

	fmtTpl := fmt.Sprintf("%s - %s\n", g("OK"), format)
	fmt.Printf(fmtTpl, args...)
}

// LogFail - prefix with colored Fail - xxxyyy
func LogFail(format string, args ...interface{}) {
	r := color.New(color.FgRed).SprintFunc()
	fmtTpl := fmt.Sprintf("%s - %s\n", r("FAIL"), format)
	fmt.Printf(fmtTpl, args...)
}

// LogError - print error directly to console
// support plain error and *errors.Error type
func LogError(err error) {
	r := color.New(color.FgRed).SprintFunc()
	if cErr, ok := err.(*errors.Error); ok {
		fmt.Printf("%s - (%d) %s: %s\n", r("FAIL"), cErr.ErrorCode, cErr.Name, cErr.Detail)
	} else {
		fmt.Printf("%s - %s\n", r("FAIL"), err.Error())
	}
}
