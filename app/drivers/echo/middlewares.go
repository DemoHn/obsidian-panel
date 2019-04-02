package echo

import (
	"github.com/labstack/echo"
	"github.com/labstack/echo/middleware"
)

func loadMiddlewares(e *echo.Echo) {
	e.Use(middleware.Logger())
	e.Use(middleware.Recover())
}
