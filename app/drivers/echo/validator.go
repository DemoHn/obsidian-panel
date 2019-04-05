package echo

import (
	"github.com/go-playground/validator"
)

type structValidator struct {
	validator *validator.Validate
}

// Validate - validate struct by tag
func (cv *structValidator) Validate(i interface{}) error {
	return cv.validator.Struct(i)
}
