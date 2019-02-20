package account

import (
	"syscall"
)

// Account - all methods about account
type Account interface {
	// New instance for this account
	New(name string, password string, group string) error
	// If user exists
	IfExists() (bool, error)
	// If in the groups given by name
	IfInGroup(group string) (bool, error)
	// Is root user
	IsRoot() (bool, error)
	// Create account and save it into OS account manager
	Create() error
	// Remove account
	Remove() error
	// inherit old sysProcAttr and add proper settings
	// so that executor would spawn process with correct user account
	SetSysProcAttr(oldAttr syscall.SysProcAttr) (syscall.SysProcAttr, error)
	// Init account privileges so that they are abled to login
	InitPrivileges() error
	// enter user context. That means all following operations are under this user
	// For Linux, it's not needed (empty function)
	EnterUserContext() error
	// exist user context
	ExitUserContext() error
}

// Group - all about groups
type Group interface {
	// New group interface
	New(group string) error
	// if group exists
	IfExists() (bool, error)
	// Create group to OS account manager
	Create() error
	// list all members of this group
	ListMembers() ([]string, error)
	// Remove group and ALL members
	Remove() error
	// Clear all members but remain this group
	// TODO: impl it (in Windows and Linux)
	// ClearAllMembers() error
}
