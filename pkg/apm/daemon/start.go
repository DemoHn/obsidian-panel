package daemon

import (
	"fmt"
	"os"
	"os/signal"
	"syscall"

	"github.com/DemoHn/obsidian-panel/pkg/apm/logger"
	"github.com/DemoHn/obsidian-panel/pkg/apm/master"
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

// handle daemon
func daemonHandler(config *cfgparser.Config, debugMode bool) error {
	var err error
	quit := make(chan os.Signal)

	// create master object
	masterN := master.New(debugMode)

	// get sockFile configlet
	var sockFile string
	if sockFile, err = config.FindString("global.sockFile"); err != nil {
		return errWithLog(err)
	}

	// init master
	if err = masterN.Init(sockFile); err != nil {
		return errWithLog(err)
	}

	go func() {
		if err = masterN.Listen(); err != nil {
			log.Errorf("[apm] daemon encounters an error on listening '%s'", sockFile)

			quit <- os.Interrupt
		}
	}()

	log.Infof("[apm] daemon start listening to '%s'", sockFile)

	// wait for quit signal
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	// 'quit' channel will receive data from two sources:
	// 1. masterN.Listen() quits with error
	// 2. parent process receives a SIGTERM signal
	// Thus if err != nil, `quit` must happens on condition #1
	if err != nil {
		return errWithLog(err)
	}

	log.Info("[apm] going to teardown")
	if err = masterN.Teardown(config); err != nil {
		return errWithLog(err)
	}

	return nil
}

// internal functions
func errWithLog(err error) error {
	// notice log must be inited before
	log.Errorf("[apm] %s", err.Error())
	return err
}
