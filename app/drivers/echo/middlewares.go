package echo

import (
	"github.com/DemoHn/obsidian-panel/infra"
	"github.com/labstack/echo"
	"github.com/labstack/echo/middleware"

	"github.com/go-playground/validator"
)

func loadMiddlewares(e *echo.Echo) {
	e.Use(middleware.Logger())
	e.Use(middleware.Recover())

	e.Use(errorHandler)
}

func errorHandler(next echo.HandlerFunc) echo.HandlerFunc {
	return func(c echo.Context) error {
		if err := next(c); err != nil {
			// wrap errors to export
			var wrapError *infra.Error

			switch e := err.(type) {
			case *infra.Error:
				wrapError = e
			case *echo.HTTPError:
				wrapError = infra.GeneralHTTPError(e.Code, e.Message)
			case validator.ValidationErrors:
				wrapError = infra.ValidationError(err)
			default:
				wrapError = infra.UnknownServerError(err)
			}

			return c.JSON(wrapError.StatusCode, wrapError)
		}
		return nil
	}
}
