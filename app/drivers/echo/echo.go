package echo

import (
	"fmt"

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

// Group - same as `echo.Group`
type Group = echo.Group

// New - new echo instance
func New(config *infra.Config) (*Driver, error) {
	var address string
	var err error

	e := echo.New()
	if address, err = config.FindString("api.address"); err != nil {
		return nil, err
	}
	// load middlewares
	loadMiddlewares(e)

	return &Driver{
		Echo:    e,
		address: address,
	}, nil
}

// GetAPIRouter - get an router instance prefix with /api/v1.0
func (drv *Driver) GetAPIRouter(version string) *Group {
	var prefix = fmt.Sprintf("/api/v%s", version)
	return drv.Echo.Group(prefix)
}

// Listen - listen to a preset port
func (drv *Driver) Listen() error {
	// hardcore first
	return drv.Start(drv.address)
}
