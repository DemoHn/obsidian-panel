package app

import (
	"github.com/DemoHn/obsidian-panel/app/drivers/gorm"
	"github.com/DemoHn/obsidian-panel/app/providers/account"
	"github.com/DemoHn/obsidian-panel/app/providers/procmanager"
	"github.com/DemoHn/obsidian-panel/infra"
)

// Providers - a set of providers that establish the core services
type Providers struct {
	Account        account.Provider
	ProcessManager procmanager.Provider
}

// Init - init app
func Init(configFile string, debugMode bool) *Providers {
	var err error

	// init logger, config
	log := infra.GetMainLogger()
	cfg := infra.GetConfig()
	// 01. set infra (config, logger)
	infra.SetMainLoggerLevel(debugMode)

	// load config file only if filename is explicitly assigned
	if configFile != "" {
		if err = infra.LoadConfig(configFile); err != nil {
			log.Errorf("Error: %s", err.Error())
			return nil
		}
	}

	// 02. init drivers
	var d *gorm.Driver
	if d, err = gorm.NewDriver(); err != nil {
		log.Errorf("Error: %s", err.Error())
		return nil
	}

	log.Info("going to upgrade core db schema")
	if err = d.SchemaUp(); err != nil {
		log.Errorf("SchemaUp Failed: %s", err.Error())
		return nil
	}
	log.Info("upgrade core db schema finish")

	// 03. init providers
	pm := procmanager.New(debugMode)
	pm.ReloadConfig(cfg)
	return &Providers{
		Account:        account.New(d),
		ProcessManager: pm,
	}
}
