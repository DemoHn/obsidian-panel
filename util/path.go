package util

import (
	"fmt"
	"os"
)

//// helpers
func FindRootPath(rootPath string) (string, error) {
	// priority:
	// 1. $rootPath
	// 2. $HOME/.obs-root

	// if rootPath is not empty, the directory must exists!
	if rootPath != "" {
		if _, err := os.Stat(rootPath); err != nil {
			return "", err
		}
	} else {
		// read $HOME
		home, err := os.UserHomeDir()
		if err != nil {
			return "", err
		}
		homePath := fmt.Sprintf("%s/.obs-root", home)
		if err := os.MkdirAll(homePath, os.ModePerm); err != nil {
			return "", err
		}
		rootPath = homePath
	}
	return rootPath, nil
}
