package api

import (
	"database/sql"
	"fmt"
	"net/http"

	"github.com/DemoHn/obsidian-panel/app/account"
	"github.com/DemoHn/obsidian-panel/app/config"
	"github.com/labstack/echo"
)

func bindConfigAPIs(cfg *config.Config, db *sql.DB, version string) {
	var prefix = fmt.Sprintf("/api/%s/config", version)
	router := server.Group(prefix, Auth(db, account.ADMIN))

	router.GET("/get-item", getItemHandler(cfg))
	router.POST("/set-item", setItemHandler(cfg))
}

func getItemHandler(cfg *config.Config) echo.HandlerFunc {
	return func(c echo.Context) error {
		req := struct {
			Key string `query:"key" validate:"required"`
		}{}
		if err := c.Bind(&req); err != nil {
			return err
		}
		if err := c.Validate(&req); err != nil {
			return err
		}

		value, err := cfg.Find(req.Key)
		if err != nil {
			return err
		}
		return c.JSON(http.StatusOK, struct {
			Data     string `json:"data"`
			TypeHint int    `json:"typeHint"`
		}{
			value.ToString(),
			value.GetTypeHint(),
		})
	}
}

func setItemHandler(cfg *config.Config) echo.HandlerFunc {
	return func(c echo.Context) error {
		req := struct {
			Key      string `json:"key" validate:"required"`
			Value    string `json:"value" validate:"required"`
			TypeHint int    `json:"typeHint" validate:"required"`
		}{}
		if err := c.Bind(&req); err != nil {
			return err
		}
		if err := c.Validate(&req); err != nil {
			return err
		}

		v := config.NewFromString(req.Value, req.TypeHint)
		if err := cfg.Set(req.Key, v); err != nil {
			return err
		}
		// get value back
		newValue, err := cfg.Find(req.Key)
		if err != nil {
			return err
		}
		return c.JSON(http.StatusOK, struct {
			Data     string `json:"data"`
			TypeHint int    `json:"typeHint"`
		}{
			newValue.ToString(),
			newValue.GetTypeHint(),
		})
	}
}
