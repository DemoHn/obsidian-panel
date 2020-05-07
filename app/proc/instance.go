package proc

import (
	"fmt"
	"os"
	"os/exec"
	"strings"
	"syscall"
	"time"

	"github.com/DemoHn/obsidian-panel/infra"
	"github.com/DemoHn/obsidian-panel/pkg/cmdspliter"
	"github.com/DemoHn/obsidian-panel/util"
)

// Instance - the basic unit of process management
type Instance struct {
	id            int
	name          string
	procSign      string
	command       string
	directory     string
	env           map[string]string
	autoStart     bool
	autoRestart   bool
	maxRetry      int
	stdoutLogFile string
	stderrLogFile string
	// protected - could not be edited by users
	// ususally for system process
	protected bool
}

// const upCount = 3 * time.Second

// StartInstance - start one instance
func StartInstance(master *Master, inst Instance) error {
	infra.Log.Infof("going to start process: %s", inst.procSign)
	fflags := NewFFlags(master.rootPath)

	pid := fflags.ReadPid(inst.procSign)
	if pid == 0 {
		infra.Log.Debugf("pid info file:%s not found, mostly there's no existing process.", fflags.getPidFile(inst.procSign))
		cmd, err := startInstance(master, inst, fflags)
		if err != nil {
			return err
		}
		// set cmd worker
		master.workers[inst.procSign] = cmd
		return nil
	}

	infra.Log.Infof("process is alreay running (pid:%d), skip execution", pid)
	return nil
}

// StopInstance - stop instance
func StopInstance(master *Master, procSign string, signal syscall.Signal) error {
	infra.Log.Infof("going to stop process: %s", procSign)
	// I. check instance
	inst, ok := master.instances[procSign]
	if !ok {
		return fmt.Errorf("process: %s not found", procSign)
	}
	// III. stop instance
	return stopInstance(master, inst, signal)
}

//// sub helpers
// start instance directly - without checking if process has
// been executed and running, rootPath is empty or not, etc...
func startInstance(master *Master, inst Instance, fflags *FFlags) (*exec.Cmd, error) {
	rootPath := master.rootPath
	// get command
	prog, args, err := cmdspliter.SplitCommand(inst.command)
	if err != nil {
		return nil, err
	}
	cmd := exec.Command(prog, args...)

	// stdout logfile
	stdlogFile, err := util.OpenFileNS(parseDir(rootPath, inst.procSign, inst.stdoutLogFile), true)
	if err != nil {
		return nil, err
	}
	stderrFile, err := util.OpenFileNS(parseDir(rootPath, inst.procSign, inst.stderrLogFile), true)
	if err != nil {
		return nil, err
	}
	cmd.Stdin = os.Stdin
	cmd.Stdout = stdlogFile
	cmd.Stderr = stderrFile
	// set wd
	if err := setCwd(cmd, rootPath, inst); err != nil {
		return nil, err
	}
	// set env
	envStrs := []string{}
	for k, v := range inst.env {
		envStrs = append(envStrs, fmt.Sprintf("%s=%s", k, v))
	}
	cmd.Env = envStrs
	// set daemon flags
	cmd.SysProcAttr = &syscall.SysProcAttr{
		Foreground: false,
		Setsid:     true,
	}
	// start cmd
	if err := cmd.Start(); err != nil {
		return nil, err
	}
	// write pid
	if err := fflags.StorePid(inst.procSign, cmd.Process.Pid); err != nil {
		return nil, err
	}
	return cmd, nil
}

// stop instance - send stop signal to an instance, wait until process is terminated
func stopInstance(master *Master, inst Instance, signal syscall.Signal) error {
	rootPath := master.rootPath
	fflags := NewFFlags(master.rootPath)
	// read pid first
	pid := fflags.ReadPid(inst.procSign)
	if pid == 0 {
		return fmt.Errorf("no active pid found")
	}

	if err := syscall.Kill(pid, signal); err != nil {
		return err
	}
	// I. find if cmd worker exists -
	cmd, ok := master.workers[inst.procSign]
	// if exists - wait for
	if ok {
		if err := cmd.Wait(); err != nil {
			return err
		}
		infra.Log.Infof("process: %s has killed successfully", inst.procSign)
		exitCode := cmd.ProcessState.ExitCode()
		infra.Log.Infof("with exitCode: %d", exitCode)
		return nil
	}

	countDown := 25
	for {
		if countDown == 0 {
			return fmt.Errorf("kill process timeout (5s)")
		}
		// III. find process
		if kerr := syscall.Kill(pid, syscall.Signal(0)); kerr != nil {
			infra.Log.Infof("process: %s has killed successfully", inst.procSign)
			util.RemoveContents(parseDir(rootPath, inst.procSign, "$rootPath/$procSign"))
			return nil
		}
		time.Sleep(200 * time.Millisecond)
		countDown = countDown - 1
	}
}

func getPidInfo() {

}

//// helper functions
// replace $rootPath, $procSign to actual values
// example:
//
// $rootPath/$procSign/access.log.tar.gz.1 =>
// /home/demohn/main-mc/access.log.tar.gz
func parseDir(rootPath string, procSign string, source string) string {
	dest := strings.Replace(source, "$rootPath", rootPath, -1)
	dest = strings.Replace(dest, "$procSign", procSign, -1)

	return dest
}

func setCwd(cmd *exec.Cmd, rootPath string, inst Instance) error {
	// set cwd - if null, use default directly
	var cwd = inst.directory
	if inst.directory == "" {
		wd, err := os.Getwd()
		if err != nil {
			return err
		}
		cwd = wd
	} else {
		cwd = parseDir(rootPath, inst.procSign, inst.directory)
	}
	cmd.Dir = cwd
	return nil
}
