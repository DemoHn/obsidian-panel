package api

import (
	"database/sql"
	"fmt"

	"github.com/DemoHn/obsidian-panel/app/config"
	"github.com/DemoHn/obsidian-panel/infra"
	"github.com/go-playground/validator"
	"github.com/labstack/echo"
	"github.com/labstack/echo/middleware"
)

// main server instance
var server *echo.Echo

// StartServer - start server process
func StartServer(cfg *config.Config, db *sql.DB) error {
	// I. use auth middlewares
	// II. get config
	host, err := cfg.Find("rpc.host")
	if err != nil {
		return err
	}
	port, err := cfg.Find("rpc.port")
	if err != nil {
		return err
	}
	vhost, _ := host.GetString()
	vport, _ := port.GetInt()
	// II. set validator MW
	address := fmt.Sprintf("%s:%d", vhost, vport)
	infra.Log.Infof("going to start server on address: %s", address)

	// III. load routes
	bindAPIs(server, db, "0.7")
	return server.Start(address)
}

func init() {
	server = echo.New()
	// III. set validator
	server.Validator = &structValidator{validator: validator.New()}
	// II. load middlewares
	server.Use(middleware.Logger())
	server.Use(middleware.Recover())

	server.Use(ErrorHandler())
}

// validator
type structValidator struct {
	validator *validator.Validate
}

// Validate - validate struct by tag
func (cv *structValidator) Validate(i interface{}) error {
	return cv.validator.Struct(i)
}
