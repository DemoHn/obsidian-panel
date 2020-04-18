package api

import (
	"database/sql"
	"fmt"
	"net/http"

	"github.com/DemoHn/obsidian-panel/app/account"
	"github.com/labstack/echo"
)

func bindAccountAPIs(server *echo.Echo, db *sql.DB, version string) {
	var prefix = fmt.Sprintf("/api/%s/accounts", version)
	rt := server.Group(prefix)
	rtAdmin := server.Group(prefix, Auth(db, account.ADMIN))
	// accounts
	rt.POST("/login", loginHandler(db))
	// list all accounts - only ADMIN could have such permission
	rtAdmin.GET("/", listAccountsHandler(db), Auth(db, account.ADMIN))
	// change password
	rtAdmin.PATCH("/password", changePasswordHandler(db), Auth(db, account.ADMIN))
	// change permission
	rtAdmin.PATCH("/permission", changePermissionHandler(db), Auth(db, account.ADMIN))
}

func loginHandler(db *sql.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		req := struct {
			Name     string `json:"name" validate:"required"`
			Password string `json:"password" validate:"required"`
		}{}
		if err := c.Bind(&req); err != nil {
			return err
		}
		if err := c.Validate(&req); err != nil {
			return err
		}

		jwt, err := account.Login(db, req.Name, req.Password)
		if err != nil {
			return err
		}
		return c.JSON(http.StatusOK, struct {
			Jwt string `json:"jwt"`
		}{jwt})
	}
}

func listAccountsHandler(db *sql.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		req := struct {
			NameLike *string `query:"name"`
			Limit    *int    `query:"limit"`
			Offset   *int    `query:"offset"`
		}{}
		if err := c.Bind(&req); err != nil {
			return err
		}
		if err := c.Validate(&req); err != nil {
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

		return c.JSON(http.StatusOK, struct {
			Total    int               `json:"total"`
			Accounts []account.Account `json:"accounts"`
		}{count, accts})
	}
}

func changePasswordHandler(db *sql.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		req := struct {
			Name     string `json:"name" validate:"required"`
			Password string `json:"password" validate:"required"`
		}{}
		if err := c.Bind(&req); err != nil {
			return err
		}
		if err := c.Validate(&req); err != nil {
			return err
		}
		// handle request
		jwt, err := account.ResetPassword(db, req.Name, req.Password)
		if err != nil {
			return err
		}

		return c.JSON(http.StatusOK, struct {
			Jwt string `json:"jwt"`
		}{jwt})
	}
}

func changePermissionHandler(db *sql.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		req := struct {
			Name       string `json:"name" validate:"required"`
			Permission string `json:"permission" validate:"oneof=ADMIN,USER"`
		}{}
		if err := c.Bind(&req); err != nil {
			return err
		}
		if err := c.Validate(&req); err != nil {
			return err
		}
		// handle request
		acct, err := account.ChangePermission(db, req.Name, req.Permission)
		if err != nil {
			return err
		}

		return c.JSON(http.StatusOK, struct {
			*account.Account
		}{acct})
	}
}
