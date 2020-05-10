package proc

import (
	"fmt"
	"io/ioutil"
	"math"
	"os/exec"
	"runtime"
	"strconv"
	"strings"
	"time"

	"github.com/DemoHn/obsidian-panel/util"
)

// EnumPidStatus - status enum
type EnumPidStatus = int

const (
	sInit       EnumPidStatus = 0
	sStarting   EnumPidStatus = 1
	sRunning    EnumPidStatus = 2
	sStopped    EnumPidStatus = 3
	sTerminated EnumPidStatus = 4
)

// ref: https://github.com/soyuka/pidusage
// Current State: only support *ix!

// PidInfo -
type PidInfo struct {
	// Status
	Status EnumPidStatus
	// Pid
	Pid int
	// CPU time in ratio * cores
	CPU float64
	// Memory (maxrss) in bytes
	Memory int64
	// Elapsed time since process start in second
	Elapsed int64
	// old cpu data
	oldCPUData cpuTimeStat
}

// internal cpuTime stat for recording historial data
type cpuTimeStat struct {
	stime  float64
	utime  float64
	uptime float64
	old    bool
}

// UpdatePidInfo -
func (m *Master) updatePidInfo(procSign string) error {
	status := getStatus(m.rootPath, procSign)
	info, ok := m.pidInfo[procSign]
	if !ok {
		info = m.resetPidInfo(procSign)
	}

	if status == sRunning {
		// OS should support
		if !supportedOS() {
			return fmt.Errorf("[NotSupported] OS:%s is not supported to get stat now", runtime.GOOS)
		}
		// get pid
		f := NewFFlags(m.rootPath)
		pid := f.ReadPid(procSign)
		startTs := f.ReadTimestamp(procSign)
		now := time.Now().Unix()
		cpuTs, stat, err := getStatOnNix(pid, info.oldCPUData)
		if err != nil {
			return err
		}
		newInfo := PidInfo{
			Status:     status,
			Pid:        pid,
			CPU:        stat.CPU,
			Memory:     stat.Memory,
			Elapsed:    now - startTs,
			oldCPUData: cpuTs,
		}
		m.pidInfo[procSign] = newInfo
		return nil
	}
	// for other states, we don't show
	newInfo := PidInfo{
		Status: status,
		oldCPUData: cpuTimeStat{
			old: true,
		},
	}
	m.pidInfo[procSign] = newInfo
	return nil
}

func (m *Master) resetPidInfo(procSign string) PidInfo {
	newInfo := PidInfo{
		Status:  sInit,
		Pid:     0,
		CPU:     0.0,
		Memory:  0,
		Elapsed: 0,
		oldCPUData: cpuTimeStat{
			stime:  0,
			utime:  0,
			uptime: 0,
			old:    true,
		},
	}
	m.pidInfo[procSign] = newInfo
	return newInfo
}

//// helpers
func getStatus(rootDir string, procSign string) EnumPidStatus {
	f := NewFFlags(rootDir)
	if f.StopExists(procSign) {
		return sStopped
	}
	if f.RetryCountExists(procSign) {
		return sTerminated
	}
	if f.TimestampExists(procSign) {
		if f.PidExists(procSign) {
			return sRunning
		}
		return sStarting
	}
	return sInit
}

// internal functions

// get supported OS
func supportedOS() bool {
	var availableOS = []string{
		"linux",
		"freebsd",
	}

	for _, os := range availableOS {
		if runtime.GOOS == os {
			return true
		}
	}

	return false
}

// get stat On *ix like systems (linux, unix)
func getStatOnNix(pid int, oldCPUData cpuTimeStat) (cpuTimeStat, PidInfo, error) {
	// TODO - new method to make memory RSS more precise!
	cpu := 0.0

	nInfo, err := parseProcfile(pid)
	if err != nil {
		return cpuTimeStat{}, PidInfo{}, err
	}
	cInfo, err := parseCPUInfo()
	if err != nil {
		return cpuTimeStat{}, PidInfo{}, err
	}

	// calculate cpu
	var total = 0.0
	var seconds = 0.0
	oldStat := oldCPUData
	childrens := nInfo.cutime + nInfo.cstime

	if oldStat.old == false {
		total = (nInfo.stime - oldStat.stime + nInfo.utime - oldStat.utime + childrens) / cInfo.clockTick
		seconds = math.Abs(float64(cInfo.uptime - oldStat.uptime))
	} else {
		total = (nInfo.stime + nInfo.utime + childrens) / cInfo.clockTick
		seconds = math.Abs(nInfo.start/cInfo.clockTick - cInfo.uptime)
	}

	if seconds > 0 {
		cpu = float64(total) / seconds
	}

	// update oldstat
	cpuTs := cpuTimeStat{
		utime:  nInfo.utime,
		stime:  nInfo.stime,
		uptime: cInfo.uptime,
		old:    false,
	}

	// read memory
	var memory = int64(nInfo.rss * cInfo.pageSize) // RSS (default)
	if memData, ok := readSmaps(pid); ok {
		memory = int64(memData * 1024) //
	}

	return cpuTs, PidInfo{
		CPU:    cpu,
		Memory: memory,
	}, nil
}

// CPU
// read procfile info

type procfileInfo struct {
	ppid   float64
	utime  float64
	stime  float64
	cutime float64
	cstime float64
	start  float64
	rss    float64
}

func parseProcfile(pid int) (*procfileInfo, error) {
	procFile := fmt.Sprintf("/proc/%d/stat", pid)

	data, err := ioutil.ReadFile(procFile)
	// e.g
	if err != nil {
		return nil, err
	}

	pInfo := &procfileInfo{}
	// parse proc file
	procstr := string(data[:])
	lastP := strings.LastIndex(procstr, ")")
	infos := strings.Split(procstr[lastP+2:], " ")

	for index, info := range infos {
		n, _ := strconv.ParseFloat(info, 64)
		switch index {
		case 1:
			pInfo.ppid = n
		case 11:
			pInfo.utime = n
		case 12:
			pInfo.stime = n
		case 13:
			pInfo.cutime = n
		case 14:
			pInfo.cstime = n
		case 19:
			pInfo.start = n
		case 21:
			pInfo.rss = n
		}
	}

	return pInfo, nil
}

type procCPUInfo struct {
	uptime    float64
	pageSize  float64
	clockTick float64
}

func parseCPUInfo() (procCPUInfo, error) {
	var clkTck float64 = 100
	var pageSize float64 = 4096

	uptimeFileBytes, err := ioutil.ReadFile("/proc/uptime")
	if err != nil {
		return procCPUInfo{}, err
	}
	uptime, _ := strconv.ParseFloat(strings.Split(string(uptimeFileBytes), " ")[0], 64)
	clkTckStdout, err := exec.Command("getconf", "CLK_TCK").Output()
	if err == nil {
		clkTck, _ = strconv.ParseFloat(strings.Split(string(clkTckStdout), "\n")[0], 64)
	}

	pageSizeStdout, err := exec.Command("getconf", "PAGESIZE").Output()
	if err == nil {
		pageSize, _ = strconv.ParseFloat(strings.Split(string(pageSizeStdout), "\n")[0], 64)
	}

	return procCPUInfo{
		uptime:    uptime,
		clockTick: clkTck,
		pageSize:  pageSize,
	}, nil
}

// return actual memory usage of pid (unit: KB)
func readSmaps(pid int) (int, bool) {
	var fdata []byte
	var err error
	rollUpFile := fmt.Sprintf("/proc/%d/smaps_rollup", pid)
	smapsFile := fmt.Sprintf("/proc/%d/smaps", pid)

	if util.FileExists(rollUpFile) {
		fdata, err = ioutil.ReadFile(rollUpFile)
		if err != nil {
			return 0, false
		}
	} else {
		fdata, err = ioutil.ReadFile(smapsFile)
		if err != nil {
			return 0, false
		}
	}

	var pssSum int
	var privateSum int
	var pssExists = false
	lines := strings.Split(string(fdata), "\n")
	for _, line := range lines {
		if strings.HasPrefix(line, "Private") {
			numS := strings.Fields(line)[1]
			num, _ := strconv.Atoi(numS)
			privateSum += num
		}
		if strings.HasPrefix(line, "Pss:") {
			numS := strings.Fields(line)[1]
			num, _ := strconv.Atoi(numS)
			pssSum += num
			pssExists = true
		}
	}

	if pssExists {
		return pssSum, true
	}
	return privateSum, true
}
