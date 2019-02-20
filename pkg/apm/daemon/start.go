package daemon

import (
	"fmt"
	"os"

	"github.com/DemoHn/obsidian-panel/pkg/apm/logger"
	"github.com/DemoHn/obsidian-panel/pkg/cfgparser"
	daemon "github.com/sevlyar/go-daemon"
)

var log = logger.GetLogger()

// Start - start the main daemon
func Start(config *cfgparser.Config, debugMode bool) error {
	var err error

	// fetch globalDir
	var globalDir string
	if globalDir, err = config.FindString("global.dir"); err != nil {
		return addTag("cfg", err)
	}

	// make directory
	if err = os.MkdirAll(globalDir, os.ModePerm); err != nil {
		return err
	}

	// init logFile & pidFile
	var pidFile, logFile string
	if pidFile, err = config.FindString("global.pidFile"); err != nil {
		return addTag("cfg", err)
	}
	if logFile, err = config.FindString("global.logFile"); err != nil {
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
	return daemonHandler(config, debugMode)
}

// StartForeground - start the apm apm daemon on foreground
// This is usually for debugging the program
func StartForeground(config *cfgparser.Config, debugMode bool) error {
	return daemonHandler(config, debugMode)
}

// internal function
func addTag(tag string, err error) error {
	return fmt.Errorf("[%s]: %s", tag, err.Error())
}
