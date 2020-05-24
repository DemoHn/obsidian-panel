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
	router.POST("/edit-instance/:procSign", editInstanceHandler(db))

	// get one instance
	router.GET("/get-instance/:procSign", getInstanceHandler(db))

	// start/stop/restart instance
	router.POST("/control-instance", controlInstanceHandler(db))
	// stat (get current instance info)
	router.GET("/stat-instance", statInstanceHandler(db))
}

// protected = 0 only
func addInstanceHandler(db *sql.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		req := proc.InstanceReq{
			AutoRestart: true, // set default value
		}
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

		inst, err := procClient.GetProcConfig(db, req.ProcSign)
		if err != nil {
			return err
		}
		return c.JSON(http.StatusOK, struct {
			Instance proc.InstanceRsp `json:"instance"`
		}{inst})
	}
}

func listInstancesHandler(db *sql.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		req := struct {
			Page  int `json:"page"`
			Count int `json:"count"`
		}{1, 20} // set default value
		if err := c.Bind(&req); err != nil {
			return err
		}

		list, err := procClient.ListAllConfigs(db, req.Page, req.Count)
		if err != nil {
			return err
		}
		totalCount, err := procClient.CountTotalList(db)
		if err != nil {
			return err
		}

		return c.JSON(http.StatusOK, struct {
			Page       int                `json:"page"`
			Count      int                `json:"count"`
			TotalCount int                `json:"totalCount"`
			List       []proc.InstanceRsp `json:"list"`
		}{req.Page, req.Count, totalCount, list})
	}
}

func editInstanceHandler(db *sql.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		procSign := c.Param("procSign")
		// then retrieve existing data from DB
		inst, err := procClient.GetProcConfig(db, procSign)
		if err != nil {
			return err
		}
		req := proc.InstanceReq{
			ProcSign:      inst.ProcSign,
			Name:          inst.Name,
			Command:       inst.Command,
			Directory:     inst.Directory,
			Env:           inst.Env,
			AutoRestart:   inst.AutoRestart,
			StdoutLogFile: inst.StdoutLogFile,
			StderrLogFile: inst.StderrLogFile,
		}
		// update req
		if err := c.Bind(&req); err != nil {
			return err
		}
		if _, uerr := procClient.EditProcConfig(db, procSign, req); uerr != nil {
			return uerr
		}
		newInst, err := procClient.GetProcConfig(db, procSign)
		if err != nil {
			return err
		}
		return c.JSON(http.StatusOK, struct {
			Instance proc.InstanceRsp `json:"instance"`
		}{newInst})
	}
}

func getInstanceHandler(db *sql.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		procSign := c.Param("procSign")
		// then retrieve existing data from DB
		inst, err := procClient.GetProcConfig(db, procSign)
		if err != nil {
			return err
		}
		return c.JSON(http.StatusOK, struct {
			Instance proc.InstanceRsp `json:"instance"`
		}{inst})
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
