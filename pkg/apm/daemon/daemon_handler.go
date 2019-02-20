package daemon

import (
	"os"
	"os/signal"
	"syscall"

	"github.com/DemoHn/obsidian-panel/pkg/apm/infra"
	"github.com/DemoHn/obsidian-panel/pkg/apm/infra/logger"
	"github.com/DemoHn/obsidian-panel/pkg/apm/mod/master"
)

// handle daemon
func daemonHandler(debugMode bool) error {
	var err error
	quit := make(chan os.Signal)

	// get config instance
	configN, log := infra.Init(nil, debugMode)

	// create master object
	masterN := master.New(debugMode)

	// get sockFile configlet
	var sockFile string
	if sockFile, err = configN.FindString("global.sockFile"); err != nil {
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
	log := logger.Get()
	log.Errorf("[apm] %s", err.Error())
	return err
}
