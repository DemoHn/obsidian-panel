package app

import (
	"github.com/DemoHn/obsidian-panel/app/drivers/gorm"
	"github.com/DemoHn/obsidian-panel/infra"
)

// Init - init app
func Init(configFile string, debugMode bool) error {
	var err error
	// 01. init infra
	var inf *infra.Infrastructure
	if inf, err = infra.New(configFile, debugMode); err != nil {
		return err
	}

	// get logger
	log := inf.GetLogger()

	// 02. init drivers
	var d *gorm.Driver
	if d, err = gorm.NewDriver(inf); err != nil {
		return err
	}

	log.Info("going to upgrade core db schema")
	if err = d.SchemaUp(); err != nil {
		return err
	}
	log.Info("upgrade core db schema finish")
	return nil
}
