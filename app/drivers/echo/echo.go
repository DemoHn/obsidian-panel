package echo

import (
	"github.com/DemoHn/obsidian-panel/infra"
	"github.com/labstack/echo"
)

// Driver - echo http driver
type Driver struct {
	*echo.Echo
	address string
}

// Context - same as `echo.Context`
type Context = echo.Context

// New - new echo instance
func New(config *infra.Config) (*Driver, error) {
	var address string
	var err error

	e := echo.New()

	if address, err = config.FindString("api.address"); err != nil {
		return nil, err
	}
	return &Driver{
		Echo:    e,
		address: address,
	}, nil
}

// Listen - listen to a preset port
func (drv *Driver) Listen() error {
	// hardcore first
	return drv.Start(drv.address)
}
