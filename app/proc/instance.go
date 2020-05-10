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
func StartInstance(master *Master, inst Instance) (*exec.Cmd, error) {
	infra.Log.Infof("going to start process: %s", inst.procSign)
	fflags := NewFFlags(master.rootPath)

	pid := fflags.ReadPid(inst.procSign)
	if pid == 0 {
		infra.Log.Debugf("pid info file:%s not found, mostly there's no existing process.", fflags.getPidFile(inst.procSign))
		cmd, err := startInstance(master, inst, fflags)
		if err != nil {
			return nil, err
		}
		// set cmd worker
		master.workers[inst.procSign] = cmd
		fflags.SetForStarting(inst.procSign)

		return cmd, nil
	}

	infra.Log.Infof("process is alreay running (pid:%d), skip execution", pid)
	return nil, nil
}

// StopInstance - stop instance
func StopInstance(master *Master, procSign string, signal syscall.Signal) (int, error) {
	infra.Log.Infof("going to stop process: %s", procSign)
	// I. check instance
	inst, ok := master.instances[procSign]
	if !ok {
		return 0, fmt.Errorf("process: %s not found", procSign)
	}
	// II. stop instance
	rtnCode, err := stopInstance(master, inst, signal)
	if err != nil {
		return rtnCode, err
	}
	NewFFlags(master.rootPath).SetForStopped(procSign)
	return rtnCode, err
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
	if err := setLogFile(cmd, rootPath, inst); err != nil {
		return nil, err
	}
	// set wd
	if err := setCwd(cmd, rootPath, inst); err != nil {
		return nil, err
	}
	setEnv(cmd, inst.env)

	// set daemon flags
	cmd.SysProcAttr = &syscall.SysProcAttr{
		Foreground: false,
		Setsid:     true,
	}
	// start cmd
	if err := cmd.Start(); err != nil {
		return nil, err
	}
	return cmd, nil
}

// stop instance - send stop signal to an instance, wait until process is terminated
func stopInstance(master *Master, inst Instance, signal syscall.Signal) (int, error) {
	fflags := NewFFlags(master.rootPath)
	// read pid first
	pid := fflags.ReadPid(inst.procSign)
	if pid == 0 {
		return 0, fmt.Errorf("no active pid found")
	}

	syscall.Kill(pid, signal)
	// I. find if cmd worker exists -
	cmd, ok := master.workers[inst.procSign]
	// if exists - wait for
	if ok {
		if err := cmd.Wait(); err != nil {
			return 0, err
		}
		infra.Log.Infof("process: %s has killed successfully", inst.procSign)
		exitCode := cmd.ProcessState.ExitCode()
		infra.Log.Infof("with exitCode: %d", exitCode)
		return exitCode, nil
	}

	countDown := 25
	for {
		if countDown == 0 {
			return 0, fmt.Errorf("kill process timeout (5s)")
		}
		// III. find process
		if kerr := syscall.Kill(pid, syscall.Signal(0)); kerr != nil {
			infra.Log.Infof("process: %s has killed successfully", inst.procSign)
			return 0, nil
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

func setEnv(cmd *exec.Cmd, env map[string]string) {
	envStrs := []string{}
	for k, v := range env {
		envStrs = append(envStrs, fmt.Sprintf("%s=%s", k, v))
	}
	cmd.Env = envStrs
}

func setLogFile(cmd *exec.Cmd, rootPath string, inst Instance) error {
	// stdout logfile
	stdlogFile, err := util.OpenFileNS(parseDir(rootPath, inst.procSign, inst.stdoutLogFile), true)
	if err != nil {
		return err
	}
	stderrFile, err := util.OpenFileNS(parseDir(rootPath, inst.procSign, inst.stderrLogFile), true)
	if err != nil {
		return err
	}
	cmd.Stdin = os.Stdin
	cmd.Stdout = stdlogFile
	cmd.Stderr = stderrFile
	return nil
}
