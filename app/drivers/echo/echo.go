package echo

import (
	"fmt"
	"strings"

	"github.com/DemoHn/obsidian-panel/app/providers/secret"
	"github.com/DemoHn/obsidian-panel/util"

	"github.com/DemoHn/obsidian-panel/infra"
	"github.com/go-playground/validator"
	"github.com/labstack/echo"
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
	return drv.Start(drv.address)
}

// Permission - compose a Middleware that checks the permission
func (drv *Driver) Permission(perms ...string) echo.MiddlewareFunc {
	return func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			// get header
			var authHeader = c.Request().Header.Get("Authorization")
			// authorize
			if len(perms) > 0 {
				rawHeader, err := parseAuthHeader(authHeader)
				if err != nil {
					return err
				}

				token, err := util.DecodeJWT(rawHeader)
				if err != nil {
					return err
				}
				/**
				// verify rawHeader
				token, err := util.VerifyAndDecodeJWT(rawHeader, secretPublicKey)
				if err != nil {
					return err
				}
				*/
				var tokPerm = token["permission"]
				// check if permission validates
				for _, p := range perms {
					if p == tokPerm {
						return next(c)
					}
				}

				return fmt.Errorf("invalid permission: %s", tokPerm)
			}
			return next(c)
		}
	}
}

// internal function
func parseAuthHeader(authHeader string) (string, error) {
	const Bearer = "Bearer "
	if strings.HasPrefix(authHeader, Bearer) {
		return authHeader[len(Bearer):], nil
	}

	return "", fmt.Errorf("invalid authorization header (should be 'Bearer' prefix)")
}
