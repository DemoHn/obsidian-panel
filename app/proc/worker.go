package proc

import (
	"fmt"
	"io/ioutil"
	"os"
	"strconv"
	"syscall"
	"time"

	"github.com/DemoHn/obsidian-panel/infra"
	"github.com/moby/moby/pkg/reexec"
)

// StartWorker -
func StartWorker(rootPath string, debug bool) error {
	logFile := fmt.Sprintf("%s/proc/obs-daemon.log", rootPath)
	pidFile := fmt.Sprintf("%s/proc/obs-daemon.pid", rootPath)

	infra.Log.Info("start obs worker...")
	cmd := reexec.Command("<obs-daemon>")
	// open log file
	fi, err := os.OpenFile(logFile, os.O_WRONLY|os.O_CREATE|os.O_APPEND, 0644)
	infra.Log.Debugf("going to open %s", logFile)
	if err != nil {
		infra.Log.Info("open obs-worker logFile failed ==")
		return err
	}
	// redirect stdout/stderr to file
	cmd.Stdin = os.Stdin
	cmd.Stdout = fi
	cmd.Stderr = fi

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
		infra.Log.Info("start obs worker failed ==")
		return err
	}

	pid := cmd.Process.Pid
	infra.Log.Debugf("start daemon pid: %d", pid)
	return ioutil.WriteFile(pidFile, []byte(strconv.Itoa(pid)), 0644)
}

func init() {
	reexec.Register("<obs-daemon>", childWorker)
	if reexec.Init() {
		os.Exit(0)
	}
}

func childWorker() {
	index := 0
	for {
		fmt.Println("testing: ", index)
		index = index + 1
		time.Sleep(1 * time.Second)
	}
}

//// helper
func bool2str(data bool) string {
	if data {
		return "1"
	}
	return "0"
}
