package api

import (
	"database/sql"
	"fmt"
	"net/http"

	"github.com/DemoHn/obsidian-panel/app/account"
	"github.com/labstack/echo"
)

func bindAPIs(server *echo.Echo, db *sql.DB, version string) {
	var prefix = fmt.Sprintf("/api/%s", version)
	router := server.Group(prefix)

	// accounts
	router.POST("/accounts/login", loginHandler(db))
	// list all accounts - only ADMIN could have such permission
	router.GET("/accounts", listAccountsHandler(db), Auth(db, account.ADMIN))
	// change password
	router.PATCH("/accounts/password", changePasswordHandler(db), Auth(db, account.ADMIN))
	// change permission
	router.PATCH("/account/permission", changePermissionHandler(db), Auth(db, account.ADMIN))
}

// LoginRequest -
type LoginRequest struct {
	Name     string `json:"name" validate:"required"`
	Password string `json:"password" validate:"required"`
}

// LoginResponse -
type LoginResponse struct {
	Jwt string `json:"jwt"`
}

func loginHandler(db *sql.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		req := new(LoginRequest)
		if err := c.Bind(req); err != nil {
			return err
		}
		if err := c.Validate(req); err != nil {
			return err
		}

		jwt, err := account.Login(db, req.Name, req.Password)
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
	Total    int               `json:"total"`
	Accounts []account.Account `json:"accounts"`
}

func listAccountsHandler(db *sql.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		req := new(ListAccountsRequest)
		if err := c.Bind(req); err != nil {
			return err
		}
		if err := c.Validate(req); err != nil {
			return err
		}

		var filter = account.AccountsFilter{
			NameLike: req.NameLike,
			Limit:    req.Limit,
			Offset:   req.Offset,
		}

		accts, err := account.ListAccountsByFilter(db, filter)
		if err != nil {
			return err
		}
		count, err := account.CountAccounts(db)
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
	Jwt string `json:"jwt"`
}

func changePasswordHandler(db *sql.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		req := new(ChangePasswordRequest)
		if err := c.Bind(req); err != nil {
			return err
		}
		if err := c.Validate(req); err != nil {
			return err
		}
		// handle request
		jwt, err := account.ResetPassword(db, req.Name, req.Password)
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
	*account.Account
}

func changePermissionHandler(db *sql.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		req := new(ChangePermissionRequest)
		if err := c.Bind(req); err != nil {
			return err
		}
		if err := c.Validate(req); err != nil {
			return err
		}
		// handle request
		acct, err := account.ChangePermission(db, req.Name, req.Permission)
		if err != nil {
			return err
		}

		return c.JSON(http.StatusOK, &ChangePermissionResponse{
			Account: acct,
		})
	}
}
