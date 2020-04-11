package main

import (
	"github.com/DemoHn/obsidian-panel/infra"
	"github.com/DemoHn/obsidian-panel/pkg/dbmigrate"
	"github.com/spf13/cobra"
)

var log = infra.GetCLILogger()

var migrateNewCmd = &cobra.Command{
	Use:   "migrate:new [file]",
	Short: "create new migration (up/down) file template",
	Args:  cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		name := args[0]
		if path, err := dbmigrate.NewTemplate(name, "app/migrations"); err != nil {
			panic(err)
		} else {
			log.PrintOK("create new migration template on: %s", path)
		}
	},
}

var migrateUpCmd = &cobra.Command{
	Use:   "migrate:up",
	Short: "update db schema to latest version",
	Run: func(cmd *cobra.Command, args []string) {

	},
}
