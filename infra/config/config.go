package config

import (
	"github.com/DemoHn/obsidian-panel/pkg/cfgparser"
)

// Config -
type Config = cfgparser.Config

// Init - init config from config dir (yaml)
func Init(configPath string) (*Config, error) {
	config := cfgparser.New("yaml")
	if err := config.Load(configPath); err != nil {
		return nil, err
	}

	return config, nil
}
