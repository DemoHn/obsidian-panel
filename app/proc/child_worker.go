package proc

import (
	"encoding/json"
	"fmt"
	"os"
	"os/signal"
	"syscall"

	"github.com/DemoHn/obsidian-panel/infra"
	"github.com/moby/moby/pkg/reexec"
)

type workerEnv struct {
	rootPath string
	debug    bool
}

//// child worker
func childWorker() error {
	// ipc data encoder
	enc := json.NewEncoder(os.NewFile(ipcPipe, "pipe"))
	// execution func of child process
	env, err := readWorkerEnv()
	if err != nil {
		sendIpcMessage(enc, "err", "open worker env error: "+err.Error())
		return err
	}
	return childCoreWorker(env, enc)
}

func childCoreWorker(env workerEnv, enc *json.Encoder) error {
	// signals
	doneErr := make(chan error, 1)
	doneOK := make(chan bool, 1)
	sig := make(chan os.Signal, 1)
	// set logger
	infra.SetMainLoggerLevel(env.debug)
	infra.Log.Debugf("rootPath=%s, debug=%v", env.rootPath, env.debug)
	// sock file
	sockFile := fmt.Sprintf("%s/proc/obs-daemon.sock", env.rootPath)

	// listen to data
	go listenToSock(sockFile, doneErr, doneOK)
	signal.Notify(sig, os.Interrupt, syscall.SIGTERM)

	// block until a signal received
	for {
		select {
		case <-sig:
			// TODO: any trim logic
			infra.Log.Info("received signal, going to close worker")
			if enc != nil {
				sendIpcMessage(enc, "ok-stop", "ok")
			}
			os.Remove(sockFile) // TODO: teardown
			return nil
		case err := <-doneErr:
			infra.Log.Debug(err)
			if enc != nil {
				sendIpcMessage(enc, "err", "listen to master error: "+err.Error())
			}
			os.Remove(sockFile)
			return err
		case <-doneOK:
			if enc != nil {
				sendIpcMessage(enc, "ok-start", "ok")
			}
		}
	}
}

func handleError(handler func() error) func() {
	return func() {
		err := handler()
		if err != nil {
			infra.Log.Error("start child worker failed: ", err.Error())
		}
	}
}

// readWorkerEnv - fetches env from os.Env
func readWorkerEnv() (workerEnv, error) {
	rootPath, _ := os.LookupEnv("OBS_DAEMON_ROOTPATH")
	debug, _ := os.LookupEnv("OBS_DAEMON_DEBUG_MODE")
	debugMode := false
	// set $HOME/.obs-root as rootPath if retrieving rootPath
	// from env is empty
	if rootPath == "" {
		home, err := os.UserHomeDir()
		if err != nil {
			return workerEnv{}, err
		}
		rootPath = fmt.Sprintf("%s/.obs-root", home)
	}
	if debug == "1" {
		debugMode = true
	}

	return workerEnv{rootPath, debugMode}, nil
}

func listenToSock(sockFile string, doneErr chan<- error, doneOK chan<- bool) {
	// start master
	master, err := NewMaster(sockFile)
	if err != nil {
		doneErr <- err
		return
	}

	infra.Log.Info("going to begin daemon master")
	if err := Listen(master, doneOK); err != nil {
		infra.Log.Error("listen to master error: ", err)
		doneErr <- err
		return
	}
}
func init() {
	reexec.Register("<obs-daemon>", handleError(childWorker))
	if reexec.Init() {
		os.Exit(0)
	}
}
