package infra

import "github.com/DemoHn/obsidian-panel/pkg/cfgparser"

var config *cfgparser.Config

// GetConfig - config getter
func GetConfig() *cfgparser.Config {
	return config
}

// LoadConfig - config setter with error
func LoadConfig(configPath string) error {
	if err := config.Load(configPath); err != nil {
		return err
	}

	return nil
}

func init() {
	config = cfgparser.New("yaml")
}

// func initDefaultConfig()
