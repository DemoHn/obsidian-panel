package proc

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"os"
	"os/exec"
	"strconv"
	"syscall"
	"time"

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

// StartDaemon - start child worker
// there're 2 types to start <obs-daemon> (i.e. the child worker):
//
// 1. run worker foreground -
func StartDaemon(rootPath string, debug bool, foreground bool) error {
	pidFile := fmt.Sprintf("%s/proc/obs-daemon.pid", rootPath)
	// DO NOT start daemon TWICE
	if exists, _ := daemonExists(pidFile); exists {
		infra.Log.Info("obs-daemon has been started")
		return nil
	}
	// 0. For foreground process, just call core function directly
	if foreground {
		return childCoreWorker(workerEnv{rootPath, debug}, nil)
	}

	// I. start worker
	infra.Log.Info("start obs worker...")
	rp, cmd, err := registerCmd(rootPath, debug)
	if err != nil {
		return err
	}

	// II. start cmd
	if err := cmd.Start(); err != nil {
		return err
	}
	// wait for background
	writePid(pidFile, cmd.Process.Pid)
	return handleIpcMessageBG(rp)
}

// KillDaemon -
func KillDaemon(rootPath string) error {
	pidFile := fmt.Sprintf("%s/proc/obs-daemon.pid", rootPath)
	sockFile := fmt.Sprintf("%s/proc/obs-daemon.sock", rootPath)

	exists, pid := daemonExists(pidFile)
	if !exists {
		infra.Log.Info("could not kill a non-existing worker process")
		return nil
	}

	// I. kill process
	if err := syscall.Kill(pid, syscall.SIGTERM); err != nil {
		return err
	}

	// II. check if sock file has been deleted
	countDown := 5
	for {
		if countDown == 0 {
			infra.Log.Error("kill daemon timeout (after 5s)")
			return nil
		}
		if !util.FileExists(sockFile) {
			infra.Log.Info("kill worker success")
			return nil
		}
		time.Sleep(500 * time.Millisecond)
		countDown = countDown - 1
	}
}

// registerCmd - only for background process
func registerCmd(rootPath string, debug bool) (*os.File, *exec.Cmd, error) {
	cmd := reexec.Command("<obs-daemon>")
	var rp *os.File
	var err error
	if rp, err = setProcPipeBG(rootPath, cmd); err != nil {
		return nil, nil, err
	}

	// II. set env
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
	return rp, cmd, nil
}

// DaemonExists - if obs-daemon has been started already
// Notice: any errors occured during reading pidFile
// will return false directly!
func daemonExists(pidFile string) (bool, int) {
	data, err := ioutil.ReadFile(pidFile)
	if err != nil {
		return false, 0
	}
	// II. get pid
	pid, err := strconv.Atoi(string(data))
	if err != nil {
		return false, 0
	}

	// III. find process
	if kerr := syscall.Kill(pid, syscall.Signal(0)); kerr != nil {
		return false, 0
	}
	return true, pid
}

// set stdin/stdout/stderr pipe (for background processes)
func setProcPipeBG(rootPath string, cmd *exec.Cmd) (*os.File, error) {
	logFile := fmt.Sprintf("%s/log/obs-daemon.log", rootPath)
	rp, wp, err := os.Pipe()
	if err != nil {
		return nil, err
	}

	// redirect stdout/stderr to log file
	fi, err := util.OpenFileNS(logFile, true)
	infra.Log.Debugf("going to open %s", logFile)
	if err != nil {
		infra.Log.Info("open obs-worker logFile failed")
		return nil, err
	}
	// redirect stdout/stderr to file
	cmd.Stdin = os.Stdin
	cmd.Stdout = fi
	cmd.Stderr = fi
	cmd.ExtraFiles = []*os.File{nil, wp}
	return rp, nil
}

// handleIpcMessageBG - when child worker started at background
// we could wait for a moment to recv message from child worker to
// indicate its status - thus we can easily realize whether it starts fail or success.
func handleIpcMessageBG(rp *os.File) error {
	// for background - recv data from child proc's ipc channel
	dec := json.NewDecoder(rp)
	for {
		var msg ipcMessage
		if err := dec.Decode(&msg); err != nil {
			return err
		}

		// handle message
		if msg.Status == "ok-start" {
			infra.Log.Info("start worker success")
			return nil
		}
		// or return fail message
		infra.Log.Info("start child worker failed:", msg.Message)
		return fmt.Errorf(msg.Message)
	}
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
