package api

import (
	"database/sql"
	"fmt"
	"net/http"
	"strconv"

	"github.com/DemoHn/obsidian-panel/app/account"
	"github.com/DemoHn/obsidian-panel/app/proc"
	procClient "github.com/DemoHn/obsidian-panel/app/proc/client"
	"github.com/labstack/echo"
)

// CtrlInstRsp -
type CtrlInstRsp struct {
	Op         string `json:"op"`
	Success    bool   `json:"success"`
	Data       int    `json:"data"`
	FailReason string `json:"failReason"`
}

// PidInfoRsp -
type PidInfoRsp struct {
	Status  string `json:"status"`
	Pid     int    `json:"pid"`
	CPU     string `json:"cpu"`
	Memory  int64  `json:"memory"`
	Elapsed int64  `json:"elapsed"`
}

func bindProcAPIs(rootPath string, db *sql.DB, version string) {
	var prefix = fmt.Sprintf("/api/%s/proc", version)
	router := server.Group(prefix, Auth(db, account.ADMIN))

	// add instance config to db
	router.POST("/add-instance", addInstanceHandler(rootPath, db))
	// list all instances config
	router.GET("/list-instances", listInstancesHandler(db))
	// edit instance config
	router.POST("/edit-instance/:procSign", editInstanceHandler(rootPath, db))
	// get one instance
	router.GET("/get-instance/:procSign", getInstanceHandler(db))
	// start/stop/restart instance
	router.POST("/control-instance/:procSign", controlInstanceHandler(rootPath, db))
	// stat (get current instance info)
	router.GET("/stat-instance/:procSign", statInstanceHandler(rootPath, db))
}

// protected = 0 only
func addInstanceHandler(rootPath string, db *sql.DB) echo.HandlerFunc {
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

		addReq := proc.AddInstanceReq{
			Override: false,
			Instance: req,
		}
		var out proc.DataRsp
		if err := procClient.SendRequest(rootPath, "Master.AddConfig", addReq, &out); err != nil {
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

func editInstanceHandler(rootPath string, db *sql.DB) echo.HandlerFunc {
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
		addReq := proc.AddInstanceReq{
			Override: true,
			Instance: req,
		}
		var out proc.DataRsp
		if err := procClient.SendRequest(rootPath, "Master.AddConfig", addReq, &out); err != nil {
			return err
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

func controlInstanceHandler(rootPath string, db *sql.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		req := struct {
			Op string `json:"op" validate:"oneof=start stop restart"`
		}{}
		procSign := c.Param("procSign")
		if err := c.Bind(&req); err != nil {
			return err
		}
		if err := c.Validate(&req); err != nil {
			return err
		}

		switch req.Op {
		case "start":
			var out proc.StartRsp
			if err := procClient.SendRequest(rootPath, "Master.Start", procSign, &out); err != nil {
				return c.JSON(http.StatusOK, CtrlInstRsp{"start", false, 0, err.Error()})
			}
			return c.JSON(http.StatusOK, CtrlInstRsp{"start", true, out.Pid, ""})
		case "stop":
			var out proc.StopRsp
			if err := procClient.SendRequest(rootPath, "Master.Stop", procSign, &out); err != nil {
				return c.JSON(http.StatusOK, CtrlInstRsp{"stop", false, 0, err.Error()})
			}
			return c.JSON(http.StatusOK, CtrlInstRsp{"stop", true, out.ReturnCode, ""})
		case "restart":
			var out proc.StartRsp
			if err := procClient.SendRequest(rootPath, "Master.Restart", procSign, &out); err != nil {
				return c.JSON(http.StatusOK, CtrlInstRsp{"start", false, 0, err.Error()})
			}
			return c.JSON(http.StatusOK, CtrlInstRsp{"start", true, out.Pid, ""})
		}
		return nil
	}
}

func statInstanceHandler(rootPath string, db *sql.DB) echo.HandlerFunc {
	var formatStatus = func(s int) string {
		switch s {
		case 0:
			return "init"
		case 1:
			return "starting"
		case 2:
			return "running"
		case 3:
			return "stopped"
		default:
			return "terminated"
		}
	}

	return func(c echo.Context) error {
		procSign := c.Param("procSign")

		var out proc.InfoRsp
		if err := procClient.SendRequest(rootPath, "Master.GetInfo", procSign, &out); err != nil {
			return err
		}

		return c.JSON(http.StatusOK, struct {
			ProcSign string     `json:"procSign"`
			Stat     PidInfoRsp `json:"stat"`
		}{
			procSign,
			PidInfoRsp{
				Status:  formatStatus(out.Status),
				Pid:     out.Pid,
				CPU:     strconv.FormatFloat(out.CPU, 'f', 4, 64),
				Memory:  out.Memory,
				Elapsed: out.Elapsed,
			},
		})
	}
}
