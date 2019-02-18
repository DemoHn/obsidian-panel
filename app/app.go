package app

import (
	"github.com/DemoHn/obsidian-panel/app/drivers/gorm"
	"github.com/DemoHn/obsidian-panel/app/providers/account"
	"github.com/DemoHn/obsidian-panel/infra"
	"github.com/DemoHn/obsidian-panel/util"
)

// Providers - a set of providers that establish the core services
type Providers struct {
	Account account.Provider
}

// Init - init app
func Init(configFile string, debugMode bool) *Providers {
	var err error
	// 01. init infra
	var inf *infra.Infrastructure
	if inf, err = infra.New(configFile, debugMode); err != nil {
		util.LogFail("%s", err.Error())
		return nil
	}

	// get logger
	log := inf.GetLogger()

	// 02. init drivers
	var d *gorm.Driver
	if d, err = gorm.NewDriver(inf); err != nil {
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
	return &Providers{
		Account: account.New(inf, d),
	}
}
