package account

import (
	"errors"
	"strings"
	"syscall"
)

// WindowsAccount - inherits Account
type WindowsAccount struct {
	// if this instance has initialized
	init     bool
	name     string
	password string
	group    string
	// windows only - token
	token uintptr
}

func objNotInitError() error {
	return errors.New("Object Instance not initialized! Please check whether you have called New(...) method")
}

// New - new instance
func (account *WindowsAccount) New(name string, password string, group string) error {
	account.init = true
	account.name = name
	account.password = password
	account.group = group
	return nil
}

// IfExists - if user exists
func (account *WindowsAccount) IfExists() (bool, error) {
	if account.init == false {
		return false, objNotInitError()
	}

	users, errorE := enumerateGroupMember(account.group)
	if errorE != nil {
		return false, errorE
	}

	found := false
	for _, v := range users {
		if strings.Compare(v, account.name) == 0 { // matched
			found = true
			break
		}
	}

	return found, nil
}

// IfInGroup -
func (account *WindowsAccount) IfInGroup(group string) (bool, error) {
	if account.init == false {
		return false, objNotInitError()
	}

	members, err := enumerateGroupMember(group)
	if err != nil {
		return false, err
	}

	found := false
	for _, v := range members {
		if strings.Compare(v, account.name) == 0 {
			found = true
			break
		}
	}

	return found, nil
}

// Create - create user (without checking if user has been created!)
func (account *WindowsAccount) Create() error {
	if account.init == false {
		return objNotInitError()
	}

	_, err := userAdd(account.name, account.name, account.password, account.group)
	if err != nil {
		return err
	}
	// set password no expire
	_, err2 := userPasswordNoExpires(account.name, true)
	if err2 != nil {
		return err2
	}

	return nil
}

// Remove - remove user
func (account *WindowsAccount) Remove() error {
	if account.init == false {
		return objNotInitError()
	}

	_, err := userDelete(account.name)
	if err != nil {
		return err
	}
	return nil
}

// SetSysProcAttr - set sysProcAttr
// Before calling 'SetSysProceAttr()' to set access token,
// Call `InitPrivileges()` to get proper privileges and thereafter get access token
func (account *WindowsAccount) SetSysProcAttr(oldAttr syscall.SysProcAttr) (syscall.SysProcAttr, error) {
	if account.init == false {
		return oldAttr, objNotInitError()
	}

	newAttr := oldAttr
	if account.token == 0 {
		return oldAttr, errors.New("SysProcAttr() Failed - invalid token")
	}

	newAttr.HideWindow = true
	newAttr.Token = syscall.Token(account.token)
	return newAttr, nil
}

// InitPrivileges - init privileges of a account
func (account *WindowsAccount) InitPrivileges() error {
	if account.init == false {
		return objNotInitError()
	}

	// add LSA Rights
	rights := []string{
		"SeBatchLogonRight",
		"SeAssignPrimaryTokenPrivilege",
		"SeIncreaseQuotaPrivilege",
	}

	err := lsaAddAccountRights(account.name, rights)
	if err != nil {
		return err
	}

	token, errLogon := logonUser(account.name, account.password)
	if errLogon != nil {
		return errLogon
	}
	// load logon token
	account.token = token

	return nil
}

// EnterUserContext - enter user context
func (account *WindowsAccount) EnterUserContext() error {
	if account.init == false {
		return objNotInitError()
	}

	if account.token == 0 {
		return errors.New("EnterUserContext() failed - Invalid token")
	}
	err := enterUserContext(account.token)
	if err != nil {
		return err
	}

	return nil
}

// ExitUserContext - exit user context
func (account *WindowsAccount) ExitUserContext() error {
	if account.init == false {
		return objNotInitError()
	}

	err := exitUserContext()
	if err != nil {
		return err
	}

	return nil
}

// WindowsGroup - windows groups
type WindowsGroup struct {
	init bool
	name string
}

// New -
func (wGroup *WindowsGroup) New(group string) error {
	wGroup.name = group
	return nil
}

// IfExists -
func (wGroup *WindowsGroup) IfExists() (bool, error) {
	if wGroup.init == false {
		return false, objNotInitError()
	}

	groups, err := enumerateGroup()
	if err != nil {
		return false, err
	}

	found := false
	for _, v := range groups {
		if strings.Compare(v, wGroup.name) == 0 {
			found = true
			break
		}
	}

	return found, nil
}

// Create -
func (wGroup *WindowsGroup) Create() error {
	if wGroup.init == false {
		return objNotInitError()
	}

	err := addGroup(wGroup.name)

	if err != nil {
		return err
	}
	return nil
}

// Remove - remove group
func (wGroup *WindowsGroup) Remove() error {
	if wGroup.init == false {
		return objNotInitError()
	}

	err := removeGroup(wGroup.name)

	if err != nil {
		return err
	}
	return nil
}

// ListMembers - list members
func (wGroup *WindowsGroup) ListMembers() ([]string, error) {
	if wGroup.init == false {
		return nil, objNotInitError()
	}

	members, err := enumerateGroupMember(wGroup.name)
	if err != nil {
		return nil, err
	}
	return members, nil
}
