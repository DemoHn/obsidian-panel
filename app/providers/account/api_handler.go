package account

import (
	"net/http"

	"github.com/DemoHn/obsidian-panel/app/drivers/echo"
)

func (p iProvider) registerAPIs() {
	e := p.echo
	router := e.GetAPIRouter("1.0")
	// register login
	router.POST("/login", loginHandler(p))
}

// internal functions

// LoginRequest -
type LoginRequest struct {
	Name     string `json:"name" validate:"required"`
	Password string `json:"password" validate:"required"`
}

// LoginResponse -
type LoginResponse struct {
	Jwt string
}

func loginHandler(p iProvider) echo.HandlerFunc {
	return func(c echo.Context) error {
		loginRequest := new(LoginRequest)
		if err := c.Bind(loginRequest); err != nil {
			return err
		}
		if err := c.Validate(loginRequest); err != nil {
			return err
		}

		jwt, err := p.Login(loginRequest.Name, loginRequest.Password)
		if err != nil {
			return err
		}
		return c.JSON(http.StatusOK, &LoginResponse{
			Jwt: jwt,
		})
	}
}
