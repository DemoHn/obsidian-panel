package procmanager

import (
	"io/ioutil"
	"strconv"
	"syscall"
	"time"

	"github.com/DemoHn/obsidian-panel/infra"

	apmDaemon "github.com/DemoHn/obsidian-panel/pkg/apm/daemon"
	"github.com/DemoHn/obsidian-panel/pkg/cfgparser"
)

// Provider - process manager (apm)
type Provider interface {
	ReloadConfig(config *cfgparser.Config) error
	StartDaemon(foreground bool) error
	PingDaemon() error
	KillDaemon(force bool) error
}

type provider struct {
	debugMode   bool
	localConfig *cfgparser.Config
}

var log = infra.GetMainLogger()

// New - new provider
func New(debugMode bool) Provider {
	localConfig := cfgparser.New("yaml")
	// loads default config
	localConfig.LoadDefault(map[string]interface{}{
		"global.dir":      "./.apm",
		"global.pidFile":  "$(global.dir)/apm.pid",
		"global.logFile":  "$(global.dir)/apm.log",
		"global.sockFile": "$(global.dir)/apm.sock",
	})

	return &provider{
		debugMode:   debugMode,
		localConfig: localConfig,
	}
}

// ReloadConfig - reload config from main configlet
func (p *provider) ReloadConfig(gConfig *cfgparser.Config) error {
	//var err error
	return nil
}

// StartDaemon - start daemon
func (p *provider) StartDaemon(foreground bool) error {
	if foreground {
		return apmDaemon.StartForeground(p.localConfig, p.debugMode)
	}
	return apmDaemon.Start(p.localConfig, p.debugMode)
}

// PingDaemon - ping daemon to ensure daemon has connected
// TODO: Config ping time
func (p *provider) PingDaemon() error {
	return apmDaemon.PingTimeout(p.localConfig, time.Second*3, time.Second*15)
}

// KillDaemon - kill daemon w/o any quit current instance logic
func (p *provider) KillDaemon(force bool) error {
	var err error
	var pidFile string
	if pidFile, err = p.localConfig.FindString("global.pidFile"); err != nil {
		return err
	}

	// read pidFile
	var pidData []byte
	if pidData, err = ioutil.ReadFile(pidFile); err != nil {
		return err
	}
	// parse to int
	var pid int
	if pid, err = strconv.Atoi(string(pidData)); err != nil {
		return err
	}

	// send quit signal (if exists)
	if force {
		return syscall.Kill(pid, syscall.SIGKILL)
	}
	if err = syscall.Kill(pid, syscall.SIGTERM); err != nil {
		return err
	}

	log.Infof("[apm] kill apm daemon (PID:%d) success", pid)
	return nil
}
