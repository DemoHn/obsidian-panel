package errors

import (
	"encoding/json"
	"fmt"
)

// Error - define an error type that extends the original one that only prints a string
type Error struct {
	Name       string `json:"name"`
	StatusCode int    `json:"-"`
	ErrorCode  int    `json:"code"`
	Detail     string `json:"detail"`
	DebugMode  bool
}

// Error - format and show error
// this is to ensure align with original `error` type
func (e *Error) Error() string {
	return fmt.Sprintf("%s(%d): %s", e.Name, e.ErrorCode, e.Detail)
}

// GetName - get error name
func (e *Error) GetName() string {
	return e.Name
}

// GetStatusCode - get statusCode [200, 404, etc.]
func (e *Error) GetStatusCode() int {
	return e.StatusCode
}

// GetErrorCode - error code
func (e *Error) GetErrorCode() int {
	return e.ErrorCode
}

// GetDetail - err detail
func (e *Error) GetDetail() string {
	return e.Detail
}

// ToJSON - transform to JSON
func (e *Error) ToJSON() ([]byte, error) {
	return json.Marshal(e)
}
