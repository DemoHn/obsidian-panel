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

// general error class

// UnknownServerError - general unknown server error
func UnknownServerError(err error) *Error {
	return &Error{
		Name:       "UnknownServerError",
		StatusCode: 500,
		ErrorCode:  50000,
		Detail:     err.Error(),
		Info:       nil,
	}
}

// ValidationError - server request validation error
func ValidationError(err error) *Error {
	return &Error{
		Name:       "ValidationError",
		StatusCode: 400,
		ErrorCode:  50001,
		Detail:     err.Error(),
		Info:       nil,
	}
}

// GeneralHTTPError - from http framework (e.g. echo)
func GeneralHTTPError(code int, info interface{}) *Error {
	return &Error{
		Name:       "GeneralHTTPError",
		StatusCode: code,
		ErrorCode:  50002,
		Detail:     fmt.Sprintf("%v", info),
		Info:       info,
	}
}
