package api

import (
	"database/sql"
	"fmt"

	"github.com/DemoHn/obsidian-panel/app/account"
	"github.com/labstack/echo"
)

func bindProcAPIs(db *sql.DB, version string) {
	var prefix = fmt.Sprintf("/api/%s/proc", version)
	router := server.Group(prefix, Auth(db, account.ADMIN))

	router.POST("/add-instance", addInstanceHandler(db))
}

// protected = 0 only
func addInstanceHandler(db *sql.DB) echo.HandlerFunc {
	return func(c echo.Context) error {
		req := struct {
			ProcSign      string            `json:"procSign" validate:"required,proc_sign"`
			Name          string            `json:"name" validate:"required,max=50"`
			Command       string            `json:"command" validate:"required"`
			Directory     string            `json:"directory validate:"-"`
			Env           map[string]string `json:"env"`
			AutoStart     bool              `json:"autoStart"`
			AutoRestart   bool              `json:"autoRestart"`
			StdoutLogFile string            `json:"stdoutLogFile"`
			StderrLogFile string            `json:"stderrLogFile"`
			MaxRetry      int               `json:"maxRetry"`
		}{}

		return nil
	}
}
