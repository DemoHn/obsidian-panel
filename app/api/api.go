package api

import (
	"fmt"

	"github.com/DemoHn/obsidian-panel/app"
	"github.com/DemoHn/obsidian-panel/infra"
	"github.com/labstack/echo"
	"github.com/labstack/echo/middleware"
)

// main server instance
var server *echo.Echo

// StartServer - start server process
func StartServer(appI *app.App) error {
	cfg := appI.GetConfig()
	db := appI.GetDB()
	rootPath := appI.GetRootPath()
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
	bindAccountAPIs(server, db, "v1")
	bindConfigAPIs(cfg, db, "v1")
	bindProcAPIs(rootPath, db, "v1")
	return server.Start(address)
}

func init() {
	server = echo.New()
	// III. set validator
	server.Validator = newValidator()
	// II. load middlewares
	server.Use(middleware.Logger())
	server.Use(middleware.Recover())

	server.Use(ErrorHandler())
}
