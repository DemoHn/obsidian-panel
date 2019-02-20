package daemon

import (
	"fmt"
	"os"

	"github.com/DemoHn/obsidian-panel/pkg/apm/infra/config"
	"github.com/DemoHn/obsidian-panel/pkg/apm/infra/logger"
	daemon "github.com/sevlyar/go-daemon"
)

// Start - start the main daemon
func Start(debugMode bool) error {
	var err error

	// since init has been done in cmd init
	configN := config.Get()
	log := logger.Get()

	// fetch globalDir
	var globalDir string
	if globalDir, err = configN.FindString("global.dir"); err != nil {
		return addTag("cfg", err)
	}

	// make directory
	if err = os.MkdirAll(globalDir, os.ModePerm); err != nil {
		return err
	}

	// init logFile & pidFile
	var pidFile, logFile string
	if pidFile, err = configN.FindString("global.pidFile"); err != nil {
		return addTag("cfg", err)
	}
	if logFile, err = configN.FindString("global.logFile"); err != nil {
		return addTag("cfg", err)
	}

	// init context
	cntxt := &daemon.Context{
		PidFileName: pidFile,
		PidFilePerm: 0644,
		LogFileName: logFile,
		LogFilePerm: 0640,
		WorkDir:     "./",
		Umask:       027,
		Args:        []string{},
	}

	var p *os.Process
	p, err = cntxt.Reborn()
	if err != nil {
		log.Debugf("[apm] daemon has started")
		return nil
	}
	// if fork process succeed, let the parent process
	// go and run the folllowing logic in the child process
	if p != nil {
		return nil
	}
	defer cntxt.Release()

	// CHILD PROCESS
	return daemonHandler(debugMode)
}

// StartForeground - start the apm apm daemon on foreground
// This is usually for debugging the program
func StartForeground(debugMode bool) error {
	return daemonHandler(debugMode)
}

// internal function
func addTag(tag string, err error) error {
	return fmt.Errorf("[%s]: %s", tag, err.Error())
}
