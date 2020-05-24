package app

import (
	"database/sql"
	"fmt"
	"os"

	"github.com/DemoHn/obsidian-panel/app/account"
	"github.com/DemoHn/obsidian-panel/app/config"
	"github.com/DemoHn/obsidian-panel/app/proc"
	procClient "github.com/DemoHn/obsidian-panel/app/proc/client"
	"github.com/DemoHn/obsidian-panel/app/sqlc"
	"github.com/DemoHn/obsidian-panel/infra"
)

// declare input params
var (
	rootPath string // if empty, use default one
	debug    bool   // enter debug mode
)

const (
	dtUser     = "admin"     // default admin user
	dtPassword = "0bs-pane1" // deafult admin password
)

// App - new app data
type App struct {
	rootPath string
	debug    bool
	db       *sql.DB
	cfg      *config.Config
}

// New - new appInstance
func New(rootPath string, debug bool) (*App, error) {
	// I. get root path
	path, err := findRootPath(rootPath)
	if err != nil {
		return nil, err
	}
	// II. init dirs
	if err := initDirs(path); err != nil {
		return nil, err
	}
	// III. open db
	db, err := FindRootDB(path)
	if err != nil {
		return nil, err
	}
	return &App{
		rootPath: path,
		debug:    debug,
		db:       db,
		cfg:      config.New(db),
	}, nil
}

// GetConfig -
func (ap *App) GetConfig() *config.Config {
	return ap.cfg
}

// GetDB -
func (ap *App) GetDB() *sql.DB {
	return ap.db
}

// Start - start app
func Start(app *App, foreground bool) error {
	infra.SetMainLoggerLevel(app.debug)
	// I. migrate up
	infra.Log.Info("establish db schema...")
	needInit, err := sqlc.MigrateInit(app.db)
	if err != nil {
		return err
	}
	// II. Load config
	infra.Log.Info("load config...")
	if err := app.cfg.Load(); err != nil {
		return err
	}

	if needInit {
		// III. inject default data
		if err := account.RegisterAdminNS(app.db, dtUser, dtPassword); err != nil {
			return err
		}
		if err := procClient.InsertSysProcess(app.db); err != nil {
			return err
		}
	}

	return proc.StartDaemon(app.rootPath, app.debug, foreground)
}

// Stop -
func Stop(app *App) error {
	infra.SetMainLoggerLevel(app.debug)
	// I.
	infra.Log.Info("going to kill panel daemon...")
	return proc.KillDaemon(app.rootPath)
}

// FindRootDB -
func FindRootDB(rootPath string) (*sql.DB, error) {
	path, err := findRootPath(rootPath)
	if err != nil {
		return nil, err
	}
	sqlFile := fmt.Sprintf("%s/sql/root.db", path)
	return sqlc.OpenDB(sqlFile)
}

//// helpers
func findRootPath(rootPath string) (string, error) {
	// priority:
	// 1. $rootPath
	// 2. $HOME/.obs-root

	// if rootPath is not empty, the directory must exists!
	if rootPath != "" {
		if _, err := os.Stat(rootPath); err != nil {
			return "", err
		}
	} else {
		// read $HOME
		home, err := os.UserHomeDir()
		if err != nil {
			return "", err
		}
		homePath := fmt.Sprintf("%s/.obs-root", home)
		if err := os.MkdirAll(homePath, os.ModePerm); err != nil {
			return "", err
		}
		rootPath = homePath
	}
	return rootPath, nil
}

func initDirs(rootPath string) error {
	var dirs = []string{
		"sql", "log", "data", "proc",
	}
	for _, dir := range dirs {
		path := fmt.Sprintf("%s/%s", rootPath, dir)
		if err := os.MkdirAll(path, os.ModePerm); err != nil {
			return err
		}
	}
	return nil
}
