package account

import (
	"github.com/DemoHn/obsidian-panel/infra"
	"github.com/DemoHn/obsidian-panel/infra/errors"
)

var accountErrors *errors.ErrorClass

func init() {
	accountErrors = infra.NewErrorClass(200)
}

// define errors

// ValidationError - triggers when a variable fails the validation
// For example: `pos` is a positive number, but `pos = -2` -> `pos < 0`,
// This fails the validation
func ValidationError(invalidCondition string) *errors.Error {
	detail := "Invalid Condition: " + invalidCondition
	return accountErrors.NewError("ValidationError", 1, 400, detail, nil)
}

// SQLExecutionError - execute SQL error, always fatal!
func SQLExecutionError(err error) *errors.Error {
	return accountErrors.NewError("SQLExecutionError", 2, 500, err.Error(), err)
}
