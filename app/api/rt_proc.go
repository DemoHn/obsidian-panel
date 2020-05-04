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
		return nil
	}
}
