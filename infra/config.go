package infra

import (
	"path/filepath"

	"github.com/DemoHn/obsidian-panel/pkg/cfgparser"
	homedir "github.com/mitchellh/go-homedir"
)

// Config -
type Config cfgparser.Config

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
	initDefaultConfig()
}

func initDefaultConfig() {
	home, _ := homedir.Dir()

	config.LoadDefault(map[string]interface{}{
		"version":        "0.7",
		"global.datadir": filepath.Join(home, ".obs"),
		"database.path":  "$(global.datadir)/sql_main.db",
		"database.type":  "sqlite",
		"apm.dir":        "$(global.datadir)/.apm",
		"apm.pidFile":    "$(global.datadir)/.apm/apm.pid",
		"apm.logFile":    "$(global.datadir)/.apm/apm.log",
		"apm.sockFile":   "$(global.datadir)/.apm/apm.sock",
	})
}
