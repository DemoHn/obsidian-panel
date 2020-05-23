package api

import (
	"database/sql"
	"fmt"
	"net/http"

	"github.com/DemoHn/obsidian-panel/app/account"
	"github.com/DemoHn/obsidian-panel/app/proc"
	"github.com/labstack/echo"
)

func bindProcAPIs(db *sql.DB, version string) {
	var prefix = fmt.Sprintf("/api/%s/proc", version)
	router := server.Group(prefix, Auth(db, account.ADMIN))

	router.POST("/add-instance", addInstanceHandler(db))
	router.GET("/list-all-instances", listInstancesHandler(db))
}

// protected = 0 only
func addInstanceHandler(db *sql.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		req := proc.InstanceReq{}
		if err := c.Bind(&req); err != nil {
			return err
		}
		if err := c.Validate(&req); err != nil {
			return err
		}
		// do logic
		if err := proc.InsertToProcConfig(db, req); err != nil {
			return err
		}
		return c.JSON(http.StatusOK, struct {
			Success bool `json:"success"`
		}{true})
	}
}

func listInstancesHandler(db *sql.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		return nil
	}
}
