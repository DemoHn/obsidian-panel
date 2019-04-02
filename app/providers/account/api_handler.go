package account

import (
	"net/http"

	"github.com/DemoHn/obsidian-panel/app/drivers/echo"
)

// LoginRequest -
type LoginRequest struct {
	Name     string `json:"name"`
	Password string `json:"password"`
}

func (p iProvider) registerAPIs() {
	e := p.echo
	router := e.GetAPIRouter("1.0")
	// register login
	router.POST("/login", func(c echo.Context) error {
		loginRequest := new(LoginRequest)

		if err := c.Bind(loginRequest); err != nil {
			return err
		}

		jwt, err := p.Login(loginRequest.Name, loginRequest.Password)
		if err != nil {
			return c.String(http.StatusBadRequest, err.Error())
		}
		return c.String(http.StatusOK, jwt)
	})
}
