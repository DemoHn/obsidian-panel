package proc

import (
	"fmt"
	"io/ioutil"
	"os"
	"os/exec"
	"strconv"
	"strings"
	"syscall"

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
func StartInstance(rootPath string, inst Instance) error {
	// I. check if rootPath is empty
	if rootPath == "" {
		return fmt.Errorf("rootPath of daemon should not be empty")
	}
	// II. get pid file
	pidFile := parseDir(rootPath, inst.procSign, "$rootPath/$procSign/pid")
	pid := getPid(pidFile)
	if pid == 0 {
		infra.Log.Debugf("pid info not found from %s, mostly there's no existing process.", pidFile)
		return startInstance(rootPath, inst)
	}

	infra.Log.Info("process is alreay running (pid:%d), skip execution", pid)
	return nil
}

//// sub helpers
// start instance directly - without checking if process has
// been executed and running, rootPath is empty or not, etc...
func startInstance(rootPath string, inst Instance) error {
	// get command
	prog, args, err := cmdspliter.SplitCommand(inst.command)
	if err != nil {
		return err
	}
	cmd := exec.Command(prog, args...)

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
	// set wd
	if err := setCwd(cmd, rootPath, inst); err != nil {
		return err
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
	return cmd.Start()
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

// getPid - read pidFile and get pid info
// if any error, then return 0
func getPid(pidFile string) int {
	if util.FileExists(pidFile) {
		data, err := ioutil.ReadFile(pidFile)
		if err != nil {
			return 0
		}
		// II. get pid
		pid, err := strconv.Atoi(string(data))
		if err != nil {
			return 0
		}
		return pid
	}
	return 0
}
