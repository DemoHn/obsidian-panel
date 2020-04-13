package main

import (
	"fmt"
	"os"

	"github.com/DemoHn/obsidian-panel/infra"
	"github.com/spf13/cobra"
)

var initCmd = &cobra.Command{
	Use:   "init",
	Short: "initialize new obsdian-panel workspace",
	RunE: func(cmd *cobra.Command, args []string) error {
		// TODO: in the future, we will migrate its logic to `obs` command
		// II. try to get path from home dir
		home, err := os.UserHomeDir()
		if err != nil {
			return err
		}

		dirs := []string{
			"%s/.obs-root",
			"%s/.obs-root/sql",
			"%s/.obs-root/proc",
		}

		// init dirs
		for _, dir := range dirs {
			if err := os.MkdirAll(fmt.Sprintf(dir, home), os.ModePerm); err != nil {
				return err
			}
		}
		// touch rootDB file
		if err := touchFile(fmt.Sprintf("%s/.obs-root/sql/root.db", home)); err != nil {
			return err
		}

		infra.LogT.PrintOK("initialize a new obsidian-panel workspace")
		return nil
	},
}

func touchFile(name string) error {
	file, err := os.OpenFile(name, os.O_RDONLY|os.O_CREATE, 0644)
	if err != nil {
		return err
	}
	file.Close()
	return nil
}
