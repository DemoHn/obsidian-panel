package proc

import (
	"fmt"
	"os"
	"os/exec"
	"strings"
	"sync"
	"syscall"
	"time"

	"github.com/DemoHn/obsidian-panel/infra"
	"github.com/DemoHn/obsidian-panel/util"
)

// InstanceHandler - main controller of instances
type InstanceHandler struct {
	rootPath  string
	instances map[string]Instance
	workers   map[string]*exec.Cmd
	pidInfo   map[string]PidInfo
	mux       sync.Mutex
}

// Instance - the basic unit of process management
type Instance struct {
	id            int
	name          string
	procSign      string
	command       string
	directory     string
	env           map[string]string
	autoRestart   bool
	maxRetry      int
	stdoutLogFile string
	stderrLogFile string
	// protected - could not be edited by users
	// ususally for system process
	protected bool
}

// NewInstanceHandler -
func NewInstanceHandler(rootPath string) *InstanceHandler {
	return &InstanceHandler{
		rootPath:  rootPath,
		instances: map[string]Instance{},
		workers:   map[string]*exec.Cmd{},
		pidInfo:   map[string]PidInfo{},
	}
}

// StartInstance -
func (ih *InstanceHandler) StartInstance(procSign string) (*exec.Cmd, error) {
	// I. find existing instance
	ih.mux.Lock()
	defer ih.mux.Unlock()

	fflags := NewFFlags(ih.rootPath)
	inst, exists := ih.instances[procSign]
	if !exists {
		return nil, fmt.Errorf("instance:%s not found", procSign)
	}
	// II. start instance
	infra.Log.Infof("going to start instance: %s", inst.procSign)

	pid := fflags.ReadPid(inst.procSign)
	// pidExists
	if pid > 0 && isPidRunning(pid) {
		infra.Log.Infof("process is alreay running (pid:%d), skip execution", pid)
		return nil, nil
	}

	fflags.SetForInit(inst.procSign)
	cmd, err := startProcess(ih.rootPath, inst)
	if err != nil {
		return nil, err
	}
	// goto starting(1) state
	ih.workers[inst.procSign] = cmd
	fflags.SetForStarting(inst.procSign)

	return cmd, nil
}

// StopInstance - stop instance
func (ih *InstanceHandler) StopInstance(procSign string, signal syscall.Signal) (int, error) {
	ih.mux.Lock()
	defer ih.mux.Unlock()

	fflags := NewFFlags(ih.rootPath)
	infra.Log.Infof("going to stop instance: %s", procSign)
	// I. check instance
	inst, ok := ih.instances[procSign]
	if !ok {
		return 0, fmt.Errorf("instance: %s not found", procSign)
	}
	// II. stop instance from pid file

	// read pid first
	pid := fflags.ReadPid(inst.procSign)
	if pid == 0 {
		return 0, fmt.Errorf("no active pid found")
	}
	// then find current worker exists... (may not exists!)
	cmd, _ := ih.workers[procSign]
	rtnCode, err := stopProcess(pid, cmd, procSign, signal)
	if err != nil {
		return rtnCode, err
	}
	// set Stopped(3) state
	fflags.SetForStopped(procSign)
	return rtnCode, err
}

//// sub helpers
// start instance directly - without checking if process has
// been executed and running, rootPath is empty or not, etc...
func startProcess(rootPath string, inst Instance) (*exec.Cmd, error) {
	// get command
	prog, args, err := SplitCommand(inst.command)
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
func stopProcess(pid int, cmd *exec.Cmd, procSign string, signal syscall.Signal) (int, error) {
	syscall.Kill(pid, signal)
	// I. find if cmd worker exists - i.e. current pid is exactly the childprocess of
	if cmd != nil {
		if err := cmd.Wait(); err != nil {
			return 0, err
		}
		exitCode := cmd.ProcessState.ExitCode()
		infra.Log.Infof("process: %s has killed successfully with exitCode=%d", procSign, exitCode)
		return exitCode, nil
	}

	// if worker not exists (i.e. obs-daemon has been restarted) - detect the status of pid by periodically check
	// if process is still running - that we could not fetch its statusCode
	err := pollingCheck(5*time.Second, 200*time.Millisecond, func(done bool) error {
		if done {
			return fmt.Errorf("kill process timeout (5s)")
		} else if !isPidRunning(pid) {
			infra.Log.Infof("process: %s has killed successfully", procSign)
			return fmt.Errorf("OK")
		}
		return nil
	})

	if err != nil && err.Error() != "OK" {
		return 0, err
	}
	return 0, nil
}

func waitForRunning(procSign string, cmd *exec.Cmd) bool {
	infra.Log.Debugf("process %s: wait 3 sec for running", procSign)

	err := pollingCheck(3*time.Second, 100*time.Millisecond, func(fin bool) error {
		if !isPidRunning(cmd.Process.Pid) {
			return fmt.Errorf("pid not running")
		}
		return nil
	})
	return err == nil
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

func isPidRunning(pid int) bool {
	if kerr := syscall.Kill(pid, syscall.Signal(0)); kerr != nil {
		return false
	}
	return true
}

func pollingCheck(total time.Duration, interval time.Duration, handler func(bool) error) error {
	for it := time.Duration(0); it <= total; it = it + interval {
		lastCall := it+interval >= total
		if err := handler(lastCall); err != nil {
			return err
		}
		time.Sleep(interval)
	}
	return nil
}
