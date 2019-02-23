package account

import (
	"github.com/DemoHn/obsidian-panel/infra"
)

var accountErrors *infra.ErrorClass

func init() {
	accountErrors = infra.NewErrorClass(200)
}

// define errors

// ValidationError - triggers when a variable fails the validation
// For example: `pos` is a positive number, but `pos = -2` -> `pos < 0`,
// This fails the validation
func ValidationError(invalidCondition string) *infra.Error {
	detail := "Invalid Condition: " + invalidCondition
	return accountErrors.NewError("ValidationError", 1, 400, detail, nil)
}

// SQLExecutionError - execute SQL error, always fatal!
func SQLExecutionError(err error) *infra.Error {
	return accountErrors.NewError("SQLExecutionError", 2, 500, err.Error(), err)
}

// CreateAccountError - insert account data failed!
func CreateAccountError(err error) *infra.Error {
	return accountErrors.NewError("CreateAccountError", 3, 400, err.Error(), err)
}
