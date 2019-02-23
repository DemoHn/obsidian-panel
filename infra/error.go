package infra

import (
	"encoding/json"
	"fmt"
)

// Error - define an error type that extends the original one that only prints a string
type Error struct {
	Name       string      `json:"name"`
	StatusCode int         `json:"-"`
	ErrorCode  int         `json:"code"`
	Info       interface{} `json:"info"`
	Detail     string      `json:"detail"`
}

// Error - format and show error
// this is to ensure align with original `error` type
func (e *Error) Error() string {
	return fmt.Sprintf("%s(%d): %s", e.Name, e.ErrorCode, e.Detail)
}

// ToJSON - transform to JSON
func (e *Error) ToJSON() ([]byte, error) {
	return json.Marshal(e)
}

// ErrorClass - a class of errors, where errorCode follows the formula:
// errCode = classCode * 100 + errNumber
type ErrorClass struct {
	ClassCode int
}

// NewError - new error under that class
func (ec *ErrorClass) NewError(name string, subCode, statusCode int, detail string, info interface{}) *Error {
	errorCode := ec.ClassCode*100 + subCode

	return &Error{
		Name:       name,
		StatusCode: statusCode,
		ErrorCode:  errorCode,
		Info:       info,
		Detail:     detail,
	}
}

// NewErrorClass - new error class
func NewErrorClass(classCode int) *ErrorClass {
	return &ErrorClass{
		ClassCode: classCode,
	}
}
