package account

import (
	"net/http"

	"github.com/DemoHn/obsidian-panel/app/drivers/echo"
	mw "github.com/DemoHn/obsidian-panel/app/middlewares"
)

// GOING TO MOVE SOMEWHERE ELSE

func (p iProvider) registerAPIs() {
	e := p.echo
	router := e.GetAPIRouter("1.0")
	// register login
	router.POST("/accounts/login", loginHandler(p))
	// list all accounts - only ADMIN could have such permission
	router.GET("/accounts", listAccountsHandler(p), mw.Auth(p.db, "ADMIN"))
	// change password
	router.PATCH("/accounts/password", changePasswordHandler(p), mw.Auth(p.db, "ADMIN"))
	// change permission
	router.PATCH("/account/permission", changePermissionHandler(p), mw.Auth(p.db, "ADMIN"))
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

// ChangePasswordRequest -
type ChangePasswordRequest struct {
	Name     string `json:"name" validate:"required"`
	Password string `json:"password" validate:"required"`
}

// ChangePasswordResponse -
type ChangePasswordResponse struct {
	Jwt string
}

func changePasswordHandler(p iProvider) echo.HandlerFunc {
	return func(c echo.Context) error {
		req := new(ChangePasswordRequest)
		if err := c.Bind(req); err != nil {
			return err
		}
		if err := c.Validate(req); err != nil {
			return err
		}
		// handle request
		jwt, err := p.ResetPassword(req.Name, req.Password)
		if err != nil {
			return err
		}

		return c.JSON(http.StatusOK, &ChangePasswordResponse{
			Jwt: jwt,
		})
	}
}

// ChangePermissionRequest -
type ChangePermissionRequest struct {
	Name       string `json:"name" validate:"required"`
	Permission string `json:"permission" validate:"oneof=ADMIN,USER"`
}

// ChangePermissionResponse -
type ChangePermissionResponse struct {
	Account *Account
}

func changePermissionHandler(p iProvider) echo.HandlerFunc {
	return func(c echo.Context) error {
		req := new(ChangePermissionRequest)
		if err := c.Bind(req); err != nil {
			return err
		}
		if err := c.Validate(req); err != nil {
			return err
		}
		// handle request
		acct, err := p.ChangePermission(req.Name, req.Permission)
		if err != nil {
			return err
		}

		return c.JSON(http.StatusOK, &ChangePermissionResponse{
			Account: acct,
		})
	}
}
