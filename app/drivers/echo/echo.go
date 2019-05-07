package echo

import (
	"fmt"

	"github.com/DemoHn/obsidian-panel/app/providers/secret"
	"github.com/DemoHn/obsidian-panel/app/middlewares"
	"github.com/DemoHn/obsidian-panel/infra"
	"github.com/go-playground/validator"
	"github.com/labstack/echo"
	echoMW "github.com/labstack/echo/middleware"
)

// Driver - echo http driver
type Driver struct {
	*echo.Echo
	address        string
	SecretProvider *secret.Provider
}

// Context - same as `echo.Context`
type Context = echo.Context

// Group - same as `echo.Group`
type Group = echo.Group

// HandlerFunc -
type HandlerFunc = echo.HandlerFunc

// New - new echo instance
func New(config *infra.Config) (*Driver, error) {
	var address string
	var err error

	e := echo.New()
	e.Validator = &structValidator{validator: validator.New()}

	if address, err = config.FindString("api.address"); err != nil {
		return nil, err
	}
	// logger & error recover
	e.Use(echoMW.Logger())
	e.Use(echoMW.Recover())

	e.Use(middlewares.Error())

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
	return drv.Start(drv.address)
}
