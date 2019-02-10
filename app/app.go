package app

import (
	"fmt"

	"github.com/DemoHn/obsidian-panel/app/drivers/gorm"
	"github.com/DemoHn/obsidian-panel/infra"
)

// Init - init app
func Init(configFile string, debugMode bool) {
	var err error
	// 01. init infra
	var inf *infra.Infrastructure
	if inf, err = infra.New(configFile, debugMode); err != nil {
		fmt.Printf("Error: %s\n", err.Error())
		return
	}

	// get logger
	log := inf.GetLogger()

	// 02. init drivers
	var d *gorm.Driver
	if d, err = gorm.NewDriver(inf); err != nil {
		log.Errorf("Error: %s", err.Error())
		return
	}

	log.Info("going to upgrade core db schema")
	if err = d.SchemaUp(); err != nil {
		log.Errorf("SchemaUp Failed: %s", err.Error())
		return
	}
	log.Info("upgrade core db schema finish")

	log.Info("TODO: run server")
}
