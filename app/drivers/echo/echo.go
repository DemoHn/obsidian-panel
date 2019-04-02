package echo

import (
	"github.com/labstack/echo"
)

// Driver - echo http driver
type Driver struct {
	*echo.Echo
}

// New - new echo instance
func New() (*Driver, error) {
	e := echo.New()

	return &Driver{e}, nil
}

// Listen - listen to a preset port
func (drv *Driver) Listen() error {
	// hardcore first
	return drv.Start(":12580")
}
