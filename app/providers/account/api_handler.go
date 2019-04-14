package account

import (
	"net/http"

	"github.com/DemoHn/obsidian-panel/app/drivers/echo"
)

func (p iProvider) registerAPIs() {
	e := p.echo
	router := e.GetAPIRouter("1.0")
	// register login
	router.POST("/accounts/login", loginHandler(p))
	router.GET("/accounts", listAccountsHandler(p), e.Permission("USER", "ADMIN"))
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

// ListAccountsRequest -
type ListAccountsRequest struct {
	NameLike *string `query:"name"`
	Limit    *int    `query:"limit"`
	Offset   *int    `query:"offset"`
}

// ListAccountsResponse -
type ListAccountsResponse struct {
	Total    int       `json:"total"`
	Accounts []Account `json:"accounts"`
}

func listAccountsHandler(p iProvider) echo.HandlerFunc {
	return func(c echo.Context) error {
		req := new(ListAccountsRequest)
		if err := c.Bind(req); err != nil {
			return err
		}
		if err := c.Validate(req); err != nil {
			return err
		}

		var filter = AccountsFilter{
			nameLike: req.NameLike,
			limit:    req.Limit,
			offset:   req.Offset,
		}

		accts, err := p.ListAccountsByFilter(filter)
		if err != nil {
			return err
		}
		count, err := p.CountAccounts()
		if err != nil {
			return err
		}

		return c.JSON(http.StatusOK, &ListAccountsResponse{
			Total:    count,
			Accounts: accts,
		})
	}
}
