package instance

import (
	"time"

	deadlock "github.com/sasha-s/go-deadlock"
)

const (
	defaultInterval = 3 * time.Second // 3s
)

// AutoRestartHandle - handle all issues about auto restart of the instance
type AutoRestartHandle struct {
	// AutoRestartInterval - the delay time to restart after which the process exited
	// This is to prevent restart too frequent
	interval time.Duration
	// the original instance
	instance    *Instance
	maskLock    bool
	restartLock bool
	mu          rwLocker
}

func newAutoRestartHandle() *AutoRestartHandle {
	return &AutoRestartHandle{
		interval:    defaultInterval,
		maskLock:    false,
		restartLock: false,
		mu:          new(deadlock.RWMutex),
	}
}

// setters
func (ar *AutoRestartHandle) setInterval(interval time.Duration) {
	ar.interval = interval
}

// Tick - trigger restart operation
func (ar *AutoRestartHandle) tick(inst *Instance) {
	autoRestart := inst.AutoRestart
	if ar.restartLock {
		// release restart lock
		ar.unforceRestart()
		// start instance immediately
		inst.Start()
		return
	}
	// else
	if autoRestart {
		go func() {
			<-time.After(ar.interval)
			if ar.maskLock == false {
				inst.Start()
			} else {
				ar.unmask()
			}
		}()
	}
}

// Mask - hide auto-restart operation temperaily
// It will work only once.
// This is usually used in restart operation
func (ar *AutoRestartHandle) mask() {
	ar.mu.Lock()
	defer ar.mu.Unlock()

	ar.maskLock = true
}

// Unmask - enable auto-restart Tick again
func (ar *AutoRestartHandle) unmask() {
	ar.mu.Lock()
	defer ar.mu.Unlock()

	ar.maskLock = false
}

func (ar *AutoRestartHandle) forceRestart() {
	ar.mu.Lock()
	defer ar.mu.Unlock()

	ar.restartLock = true
}

func (ar *AutoRestartHandle) unforceRestart() {
	ar.mu.Lock()
	defer ar.mu.Unlock()

	ar.restartLock = false
}
