package config

import (
	"github.com/DemoHn/obsidian-panel/pkg/cfgparser"
)

// Init - init config from config dir (yaml)
func Init(configPath string) (*cfgparser.Config, error) {
	config := cfgparser.New("yaml")
	if err := config.Load(configPath); err != nil {
		return nil, err
	}

	return config, nil
}
