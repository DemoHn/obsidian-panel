package proc

import (
	"fmt"
	"io/ioutil"
	"os"
	"strconv"
	"time"

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

// SetForInit - set flags for init(0) state
func (f *FFlags) SetForInit(procSign string) {
	// clear all files
	f.RemovePid(procSign)
	f.RemoveTimestamp(procSign)
	f.RemoveStop(procSign)
}

// SetForStarting - set flags for starting(1) state
func (f *FFlags) SetForStarting(procSign string) {
	f.RemovePid(procSign)
	f.RemoveStop(procSign)
	f.StoreTimestamp(procSign)
}

// SetForRunning - from starting(1) -> running(2) state
func (f *FFlags) SetForRunning(procSign string, pid int) {
	f.StorePid(procSign, pid)
}

// SetForStopped - from running(2) -> stopped(3) state
func (f *FFlags) SetForStopped(procSign string) {
	f.RemovePid(procSign)
	f.RemoveRetryCount(procSign)
	f.RemoveTimestamp(procSign)
	f.StoreStop(procSign)
}

// SetForTerminated - from running(2), starting(1) -> terminated(4) state
func (f *FFlags) SetForTerminated(procSign string) {
	f.RemovePid(procSign)
	f.RemoveTimestamp(procSign)
	f.RemoveStop(procSign)
	f.AddRetryCount(procSign)
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

// RemovePid - remove pid file
func (f *FFlags) RemovePid(procSign string) error {
	return os.Remove(f.getPidFile(procSign))
}

// PidExists -
func (f *FFlags) PidExists(procSign string) bool {
	return util.FileExists(f.getPidFile(procSign))
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

// RemoveRetryCount -
func (f *FFlags) RemoveRetryCount(procSign string) error {
	return os.Remove(f.getRetryFile(procSign))
}

// RetryCountExists -
func (f *FFlags) RetryCountExists(procSign string) bool {
	return util.FileExists(f.getRetryFile(procSign))
}

// StoreTimestamp -
func (f *FFlags) StoreTimestamp(procSign string) error {
	tsFile := f.getTsFile(procSign)
	tsStr := strconv.FormatInt(time.Now().Unix(), 10)

	return util.WriteFileNS(tsFile, false, []byte(tsStr))
}

// ReadTimestamp -
func (f *FFlags) ReadTimestamp(procSign string) int64 {
	tsFile := f.getTsFile(procSign)
	if util.FileExists(tsFile) {
		q, _ := ioutil.ReadFile(tsFile)
		r, _ := strconv.ParseInt(string(q), 10, 64)
		return r
	}
	return 0
}

// RemoveTimestamp -
func (f *FFlags) RemoveTimestamp(procSign string) error {
	tsFile := f.getTsFile(procSign)
	return os.Remove(tsFile)
}

// TimestampExists -
func (f *FFlags) TimestampExists(procSign string) bool {
	return util.FileExists(f.getTsFile(procSign))
}

// StoreStop -
func (f *FFlags) StoreStop(procSign string) error {
	stopFile := f.getStopFile(procSign)
	return util.WriteFileNS(stopFile, false, []byte("1"))
}

// RemoveStop -
func (f *FFlags) RemoveStop(procSign string) error {
	tsFile := f.getStopFile(procSign)
	return os.Remove(tsFile)
}

// StopExists -
func (f *FFlags) StopExists(procSign string) bool {
	return util.FileExists(f.getStopFile(procSign))
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

func (f *FFlags) getStopFile(procSign string) string {
	return fmt.Sprintf("%s/%s/stop", f.rootDir, procSign)
}
