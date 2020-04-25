package proc

import (
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"os/signal"
	"strconv"
	"syscall"

	"github.com/DemoHn/obsidian-panel/infra"
	"github.com/DemoHn/obsidian-panel/util"
	"github.com/moby/moby/pkg/reexec"
)

const (
	ipcPipe = 4
)

type ipcMessage struct {
	Status  string `json:"status"`
	Message string `json:"message"`
}

// StartDaemon -
func StartDaemon(rootPath string, debug bool, foreground bool) error {
	pidFile := fmt.Sprintf("%s/proc/obs-daemon.pid", rootPath)

	// I. start worker
	infra.Log.Info("start obs worker...")
	cmd := reexec.Command("<obs-daemon>")

	// III. set pipes
	// create r/w pipe pair for child/parent process communication
	rp, wp, err := os.Pipe()
	if err != nil {
		return err
	}
	setProcPipe(rootPath, cmd, foreground, wp)

	// IV. set env
	cmd.Env = append(cmd.Env,
		fmt.Sprintf("OBS_DAEMON_ROOTPATH=%s", rootPath),
		fmt.Sprintf("OBS_DAEMON_DEBUG_MODE=%s", bool2str(debug)),
	)
	infra.Log.Debugf("obs worker env: %+v", cmd.Env)

	// set daemon flags
	cmd.SysProcAttr = &syscall.SysProcAttr{
		Foreground: false,
		Setsid:     true,
	}
	if err := cmd.Start(); err != nil {
		infra.Log.Error("start obs worker failed")
		return err
	}
	// V. write pid
	writePid(pidFile, cmd.Process.Pid)
	defer os.Remove(pidFile)

	// VI. wait or listen sock
	if foreground {
		if err := cmd.Wait(); err != nil {
			infra.Log.Error("wait obs worker failed")
			return err
		}
		return nil
	}

	dec := json.NewDecoder(rp)
	for {
		var msg ipcMessage
		if err := dec.Decode(&msg); err != nil {
			return err
		}

		// handle message
		if msg.Status == "ok" {
			infra.Log.Info("start worker success")
			return nil
		} else {
			infra.Log.Info("start child worker failed:", msg.Message)
			return err
		}
	}
}

//// child worker
func childWorker() {
	// execution func of child process
	var rootPath = ""
	var debugMode = "0"
	// I. load env
	rootPath, _ = os.LookupEnv("OBS_DAEMON_ROOTPATH")
	debugMode, _ = os.LookupEnv("OBS_DAEMON_DEBUG_MODE")
	var isDebug = false
	if debugMode == "1" {
		isDebug = true
	}
	// set logger
	infra.SetMainLoggerLevel(isDebug)
	infra.Log.Debugf("rootPath=%s, debugMode=%s", rootPath, debugMode)
	// set root path
	if rootPath == "" {
		infra.Log.Error("rootPath is empty, stop execute worker")
		return
	}

	// ipc pipe
	enc := json.NewEncoder(os.NewFile(ipcPipe, "pipe"))

	var sockFile = fmt.Sprintf("%s/proc/obs-daemon.sock", rootPath)
	master, err := NewMaster(sockFile)
	if err != nil {
		infra.Log.Error("create master error:", err)
		// ignore errors of sendIpcMessage()
		sendIpcMessage(enc, "err", "create master error: "+err.Error())
		return
	}

	doneErr := make(chan error, 1)
	doneOK := make(chan bool, 1)
	sig := make(chan os.Signal, 1)
	signal.Notify(sig, syscall.SIGHUP, syscall.SIGTERM)
	// listen to data
	go func() {
		infra.Log.Info("going to begin daemon master")
		if err := Listen(master, doneOK); err != nil {
			infra.Log.Error("listen to master error:", err)
			doneErr <- err
		}
	}()

	// block until a signal received
	for {
		select {
		case <-sig:
			// TODO: any trim logic
			infra.Log.Info("received signal, going to close worker")
			return
		case err := <-doneErr:
			sendIpcMessage(enc, "err", "listen to master error: "+err.Error())
			return
		case <-doneOK:
			sendIpcMessage(enc, "ok", "ok")
		}
	}
}

// set stdin/stdout/stderr pipe
func setProcPipe(rootPath string, cmd *exec.Cmd, foreground bool, wp *os.File) error {
	var logFile = fmt.Sprintf("%s/log/obs-daemon.log", rootPath)
	if foreground {
		cmd.Stdin = os.Stdin
		cmd.Stdout = os.Stdout
		cmd.Stderr = os.Stdout
	} else {
		// redirect stdout/stderr to log file
		fi, err := util.OpenFileNS(logFile, true)
		infra.Log.Debugf("going to open %s", logFile)
		if err != nil {
			infra.Log.Info("open obs-worker logFile failed")
			return err
		}
		// redirect stdout/stderr to file
		cmd.Stdin = os.Stdin
		cmd.Stdout = fi
		cmd.Stderr = fi
	}
	cmd.ExtraFiles = []*os.File{nil, wp}
	return nil
}

func sendIpcMessage(enc *json.Encoder, status string, message string) error {
	ipcMsg := ipcMessage{
		Status:  status,
		Message: message,
	}
	return enc.Encode(&ipcMsg)
}

//// helpers
func bool2str(data bool) string {
	if data {
		return "1"
	}
	return "0"
}

func writePid(pidFile string, pid int) error {
	infra.Log.Debugf("start daemon pid: %d", pid)
	return util.WriteFileNS(pidFile, false, []byte(strconv.Itoa(pid)))
}

func init() {
	reexec.Register("<obs-daemon>", childWorker)
	if reexec.Init() {
		os.Exit(0)
	}
}
