package app

import (
	"github.com/DemoHn/obsidian-panel/app/drivers"
	"github.com/DemoHn/obsidian-panel/app/providers"
	"github.com/DemoHn/obsidian-panel/infra"
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

// internal functions
func beforeSetup(config *infra.Config, drv *drivers.Drivers, prv *providers.Providers) error {
	var err error
	log := infra.GetMainLogger()

	log.Info("going to upgrade core db schema")
	if err = drv.Sqlite.SchemaUp(); err != nil {
		return err
	}
	log.Info("upgrade core db schema finish")

	// 02. generate new secret key if not exists
	if _, err = prv.Secret.GetFirstSecretKey(); err != nil {
		// if key is empty
		if err = prv.Secret.NewSecretKey(); err != nil {
			return err
		}
	}

	// 03. reload process manager config
	prv.ProcessManager.ReloadConfig(config)
	return nil
}
