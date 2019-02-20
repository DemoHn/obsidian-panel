// +build linux nacl netbsd openbsd solaris

package account

import (
	"errors"
	"fmt"
	"os/exec"
	"os/user"
	"strings"
	"syscall"
)

const chpasswdCmd = "chpasswd"
const useraddCmd = "useradd"

// UnixAccount - unix account type
type UnixAccount struct {
	init     bool
	name     string
	password string
	group    string
}

// <internal function>
func execSync(program string, args ...string) (int, error) {
	cmd := exec.Command(program, args...)
	err := cmd.Run()
	// if success
	if err == nil {
		return 0, nil
	}

	// else get status code
	if serr, ok := err.(*exec.ExitError); ok {
		if ws, ok2 := serr.Sys().(syscall.WaitStatus); ok2 {
			exitCode := ws.ExitStatus()
			return exitCode, nil
		}
		return -1, fmt.Errorf("get errCode failed")
	}
	return -1, err
}

func objNotInitError() error {
	return errors.New("Object Instance not initialized! Please check whether you have called New(...) method")
}

// New - new instance
func (account *UnixAccount) New(name string, password string, group string) error {
	// check if related command exists
	code1, err1 := execSync("command", "-v", useraddCmd)
	if err1 != nil {
		return err1
	}
	if code1 != 0 {
		return fmt.Errorf("command %s not found", useraddCmd)
	}
	// ...and chpasswd
	code2, err2 := execSync("command", "-v", chpasswdCmd)
	if err2 != nil {
		return err2
	}
	if code2 != 0 {
		if code1 != 0 {
			return fmt.Errorf("command %s not found", chpasswdCmd)
		}
	}
	// if all commands exists...
	account.init = true
	account.name = name
	account.password = password
	account.group = group
	return nil
}

// IfExists - if user exists
func (account *UnixAccount) IfExists() (bool, error) {
	if account.init == false {
		return false, objNotInitError()
	}

	_, err := user.Lookup(account.name)
	if err != nil {
		return false, err
	}

	return true, nil
}

// IfInGroup - if user is in the group given by name
func (account *UnixAccount) IfInGroup(group string) (bool, error) {
	if account.init == false {
		return false, objNotInitError()
	}

	// get user instance first
	lUser, err := user.Lookup(account.name)
	if err != nil {
		return false, err
	}
	// then find group id
	lGroup, err2 := user.LookupGroup(group)
	if err2 != nil {
		return false, err2
	}
	// find all local groups
	groupIds, err3 := lUser.GroupIds()
	if err3 != nil {
		return false, err3
	}
	// now it's time to check if groupId in groupIds
	found := false
	for _, groupId := range groupIds {
		if strings.Compare(groupId, lGroup.Gid) == 0 {
			found = true
			break
		}
	}

	return found, nil
}

// Create user - TODO
func (account *UnixAccount) Create() error {
	if account.init == false {
		return objNotInitError()
	}
	// exec 'useradd' command
	//execSync()
	return nil
}

// Remove - TODO
func (account *UnixAccount) Remove() error {
	if account.init == false {
		return objNotInitError()
	}
	return nil
}

// SetSysProcAttr -
func (account *UnixAccount) SetSysProcAttr(oldAttr syscall.SysProcAttr) (syscall.SysProcAttr, error) {
	if account.init == false {
		return oldAttr, objNotInitError()
	}
	return oldAttr, nil
}

// Leave it blank, since it's not needed
func (account *UnixAccount) InitPrivileges() error {
	if account.init == false {
		return objNotInitError()
	}
	return nil
}

func (account *UnixAccount) EnterUserContext() error {
	if account.init == false {
		return objNotInitError()
	}
	return nil
}

func (account *UnixAccount) ExitUserContext() error {
	if account.init == false {
		return objNotInitError()
	}
	return nil
}

type UnixGroup struct {
	init bool
	name string
}
