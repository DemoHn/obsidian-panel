package api

import (
	"database/sql"
	"fmt"
	"net/http"

	"github.com/DemoHn/obsidian-panel/app/account"
	"github.com/DemoHn/obsidian-panel/app/proc"
	procClient "github.com/DemoHn/obsidian-panel/app/proc/client"
	"github.com/labstack/echo"
)

func bindProcAPIs(db *sql.DB, version string) {
	var prefix = fmt.Sprintf("/api/%s/proc", version)
	router := server.Group(prefix, Auth(db, account.ADMIN))

	// add instance config to db
	router.POST("/add-instance", addInstanceHandler(db))
	// list all instances config
	router.GET("/list-instances", listInstancesHandler(db))
	// edit instance config
	router.POST("/edit-instance", editInstanceHandler(db))
	// start/stop/restart instance
	router.POST("/control-instance", controlInstanceHandler(db))
	// stat (get current instance info)
	router.GET("/stat-instance", statInstanceHandler(db))
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
		if err := procClient.InsertToProcConfig(db, req); err != nil {
			return err
		}
		return c.JSON(http.StatusOK, struct {
			Success bool `json:"success"`
		}{true})
	}
}

func listInstancesHandler(db *sql.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		data, err := procClient.ListAllConfigs(db)
		if err != nil {
			return err
		}

		return c.JSON(http.StatusOK, data)
	}
}

func editInstanceHandler(db *sql.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		return nil
	}
}

func controlInstanceHandler(db *sql.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		return nil
	}
}

func statInstanceHandler(db *sql.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		return nil
	}
}
