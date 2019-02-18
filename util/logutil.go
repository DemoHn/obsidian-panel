package util

// logUtil is used for logging in CLI interface
import (
	"fmt"

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
