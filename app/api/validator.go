package api

import "github.com/go-playground/validator"

// validator
type structValidator struct {
	validator *validator.Validate
}

// Validate - validate struct by tag
func (cv *structValidator) Validate(i interface{}) error {
	return cv.validator.Struct(i)
}

func newValidator() *structValidator {
	v := &structValidator{validator: validator.New()}
	v.validator.RegisterValidation("proc_sign", validateProcSign)
	return v
}

//// custom validation function

// usage: proc_sign
//
// how: all chars of proc_sign is one of [a-zA-Z0-9_-]
func validateProcSign(fl validator.FieldLevel) bool {
	chars := []rune(fl.Field().String())
	for _, ch := range chars {
		res := (ch >= '0' && ch <= '9') ||
			(ch >= 'a' && ch <= 'z') ||
			(ch >= 'A' && ch <= 'Z') ||
			ch == '_' ||
			ch == '-'

		if !res {
			return res
		}
	}
	return true
}
