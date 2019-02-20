package daemon

import (
	"os"
	"os/signal"
	"syscall"

	"github.com/DemoHn/obsidian-panel/pkg/apm/master"
	"github.com/DemoHn/obsidian-panel/pkg/cfgparser"
)

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
	if err = masterN.Teardown(); err != nil {
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
