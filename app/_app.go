package app

import (
	"database/sql"
	"fmt"
	"os"

	"github.com/DemoHn/obsidian-panel/app/drivers"
	"github.com/DemoHn/obsidian-panel/app/providers"
	"github.com/DemoHn/obsidian-panel/infra"
	"github.com/spf13/cobra"

	// import sqlite3
	_ "github.com/mattn/go-sqlite3"
)

// App - main app
type App struct {
	*drivers.Drivers
	*providers.Providers
}

// New - create a new app instance, with drivers & providers initialized
func New(configFile string, debugMode bool) (*App, error) {
	var err error

	cfg := infra.GetConfig()
	infra.SetMainLoggerLevel(debugMode)
	// load config file only if filename is explicitly assigned
	if configFile != "" {
		if err = infra.LoadConfig(configFile); err != nil {
			return nil, err
		}
	}
	// 01. init drivers
	var drv *drivers.Drivers
	if drv, err = drivers.Init(cfg); err != nil {
		return nil, err
	}
	// 02. init providers
	var prv *providers.Providers
	if prv, err = providers.Init(drv); err != nil {
		return nil, err
	}
	// 03. before setup
	if err = beforeSetup(cfg, drv, prv); err != nil {
		return nil, err
	}

	return &App{
		Drivers:   drv,
		Providers: prv,
	}, nil
}

// GetProviders - get (initialized) app providers
func (app *App) GetProviders() *providers.Providers {
	return app.Providers
}

// GetDrivers - get (initialized) app drivers
func (app *App) GetDrivers() *drivers.Drivers {
	return app.Drivers
}

// Start - start application
func (app *App) Start() error {
	return app.Drivers.Echo.Listen()
}

// LoadAppFromCmd - init and get app instance from cobra.Command object
// directly. This is usually for further manipulation after app initialized.
func LoadAppFromCmd(cmd *cobra.Command) (*App, error) {
	app, err := loadAppFromCmd(cmd)
	if err != nil {
		return nil, err
	}

	return app, nil
}

// LoadProvidersFromCmd - init app and get providers from cobra.Command object
// directly. This is usually for further manipulation after app initialized.
func LoadProvidersFromCmd(cmd *cobra.Command) (*providers.Providers, error) {
	app, err := loadAppFromCmd(cmd)
	if err != nil {
		return nil, err
	}

	return app.GetProviders(), nil
}

// internal functions
func beforeSetup(config *infra.Config, drv *drivers.Drivers, prv *providers.Providers) error {
	var err error
	log := infra.GetMainLogger()

	log.Info("going to upgrade core db schema")
	if err = drv.Sqlite.SchemaUp(); err != nil {
		return err
	}
	log.Info("upgrade core db schema finish")
	// 02. load secret provider?

	// 03. reload process manager config
	prv.ProcessManager.ReloadConfig(config)
	return nil
}

func loadAppFromCmd(cmd *cobra.Command) (*App, error) {
	var err error
	var configPath = ""
	var debugMode = false

	// init flags
	flagset := cmd.Flags()
	if configPath, err = flagset.GetString("config"); err != nil {
		return nil, err
	}
	if debugMode, err = flagset.GetBool("debug"); err != nil {
		return nil, err
	}

	var appInstance *App
	if appInstance, err = New(configPath, debugMode); err != nil {
		return nil, err
	}

	return appInstance, nil
}

//// helpers

// FindRootDB - Find root DB location and open it
func FindRootDB(dbFile *string) (*sql.DB, error) {
	// if dbFile is empty, then we will attempt to find rootDB from the
	// following dirs:
	//
	// 1. $HOME/.obs-root/sql/root.db
	// 2. $CWD/data/sql/root.db
	//
	// An error will be thrown if both locations are not found.

	// I. first try to open DB from predefined dbFile
	if dbFile != nil {
		path := *dbFile
		return sql.Open("sqlite3", path)
	}

	// II. try to get path from home dir
	home, err := os.UserHomeDir()
	if err != nil {
		return nil, err
	}
	pathII := fmt.Sprintf("%s/.obs-root/sql/root.db", home)
	if _, err := os.Stat(pathII); os.IsNotExist(err) {
		// III. try to get path from data dir
		wd, err := os.Getwd()
		if err != nil {
			return nil, err
		}
		pathIII := fmt.Sprintf("%s/data/sql/root.db", wd)
		if _, err := os.Stat(pathIII); os.IsNotExist(err) {
			return nil, err
		}
		return sql.Open("sqlite3", pathIII)
	}
	return sql.Open("sqlite3", pathII)
}
