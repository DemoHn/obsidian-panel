package proc

import (
	"fmt"
	"net"
	"os"
	"strconv"
	"strings"
	"syscall"

	"github.com/DemoHn/obsidian-panel/infra"
	"github.com/DemoHn/obsidian-panel/util"
	"github.com/moby/moby/pkg/reexec"
)

// StartDaemon -
func StartDaemon(rootPath string, debug bool, foreground bool) error {
	logFile := fmt.Sprintf("%s/log/obs-daemon.log", rootPath)
	pidFile := fmt.Sprintf("%s/proc/obs-daemon.pid", rootPath)
	sockFile := fmt.Sprintf("%s/proc/obs-daemon-recv.sock", rootPath)

	// I. start worker
	infra.Log.Info("start obs worker...")
	cmd := reexec.Command("<obs-daemon>")

	// III. set log
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
			infra.Log.Error("wait obs worker failed:")
			return err
		}
		return nil
	}
	// do on background
	if err := util.InitFileDir(sockFile); err != nil {
		return err
	}
	ln, err := net.Listen("unix", sockFile)
	if err != nil {
		infra.Log.Debugf("listen recv sock error ==")
		return err
	}
	for {
		b := make([]byte, 1024)
		conn, err := ln.Accept()
		if err != nil {
			return err
		}
		conn.Read(b)
		if strings.Contains(string(b), "OK") {
			infra.Log.Info("done!")
			break
		}
	}

	return nil
}

func init() {
	reexec.Register("<obs-daemon>", childWorker)
	if reexec.Init() {
		os.Exit(0)
	}
}

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
		infra.Log.Error("rootPath is empty, stop executing further logic")
		return
	}
	var sockFile = fmt.Sprintf("%s/proc/obs-daemon.sock", rootPath)
	master, err := NewMaster(sockFile)
	if err != nil {
		infra.Log.Error("create master error:", err)
		return
	}

	infra.Log.Info("going to begin daemon master")
	if err := Listen(master); err != nil {
		infra.Log.Error("listen to master error:", err)
		return
	}
}

//// helper
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
