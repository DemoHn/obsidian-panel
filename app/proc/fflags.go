package proc

import (
	"fmt"
	"io/ioutil"
	"strconv"

	"github.com/DemoHn/obsidian-panel/util"
)

// FFlags represents for File-formed flags, which is a common way to store process related
// info (e.g. pid, retry times, stop sign) by plain text files.
//
// for example:
// FILE `$rootPath/$procSign/pid` -> 22501 (that means currently running pid of proc $procSign is 22501)
type FFlags struct {
	rootDir string
}

// NewFFlags -
func NewFFlags(rootDir string) *FFlags {
	return &FFlags{
		rootDir: rootDir,
	}
}

// StorePid - store pid data
func (f *FFlags) StorePid(procSign string, pid int) error {
	pidFile := f.getPidFile(procSign)
	pidStr := strconv.Itoa(pid)

	return util.WriteFileNS(pidFile, false, []byte(pidStr))
}

// ReadPid - read pid data. return 0 if any error
func (f *FFlags) ReadPid(procSign string) int {
	pidFile := f.getPidFile(procSign)
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

// ReadRetryCount -
func (f *FFlags) ReadRetryCount(procSign string) int {
	retryFile := f.getRetryFile(procSign)
	if util.FileExists(retryFile) {
		q, _ := ioutil.ReadFile(retryFile)
		r, _ := strconv.Atoi(string(q))
		return r
	}
	return 0
}

// AddRetryCount - if retryFile is empty, write 1 to retryFile directly
func (f *FFlags) AddRetryCount(procSign string) (int, error) {
	var data = 1
	retryFile := f.getRetryFile(procSign)
	if util.FileExists(retryFile) {
		// read data first
		q, err := ioutil.ReadFile(retryFile)
		if err != nil {
			return 0, err
		}
		r, _ := strconv.Atoi(string(q))
		data = r + 1
	}

	dataStr := strconv.Itoa(data)
	if err := util.WriteFileNS(retryFile, false, []byte(dataStr)); err != nil {
		return 0, err
	}
	return data, nil
}

// ResetRetryCount -
func (f *FFlags) ResetRetryCount(procSign string) error {
	retryFile := f.getRetryFile(procSign)
	return util.WriteFileNS(retryFile, false, []byte("0"))
}

//// helpers
func (f *FFlags) getPidFile(procSign string) string {
	return fmt.Sprintf("%s/%s/pid", f.rootDir, procSign)
}

func (f *FFlags) getRetryFile(procSign string) string {
	return fmt.Sprintf("%s/%s/retry", f.rootDir, procSign)
}

func (f *FFlags) getTsFile(procSign string) string {
	return fmt.Sprintf("%s/%s/timestamp", f.rootDir, procSign)
}
