package main

import (
	"github.com/DemoHn/obsidian-panel/app"
	"github.com/DemoHn/obsidian-panel/infra"
	"github.com/DemoHn/obsidian-panel/pkg/dbmigrate"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
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
	RunE: func(cmd *cobra.Command, args []string) error {
		dbPath, _ := viper.Get("db").(string)
		var target *string

		if dbPath != "" {
			target = &dbPath
		}
		db, err := app.FindRootDB(target)
		if err != nil {
			return err
		}
		if err := dbmigrate.Up(db); err != nil {
			return err
		}

		log.PrintOK("migrate up done")
		return nil
	},
}

var migrateDownCmd = &cobra.Command{
	Use:   "migrate:down",
	Short: "migrate db schema down to its initial state",
	RunE: func(cmd *cobra.Command, args []string) error {
		dbPath, _ := viper.Get("db").(string)
		var target *string

		if dbPath != "" {
			target = &dbPath
		}
		db, err := app.FindRootDB(target)
		if err != nil {
			return err
		}
		if err := dbmigrate.Down(db); err != nil {
			return err
		}

		log.PrintOK("migrate down done")
		return nil
	},
}

func init() {
	migrateUpCmd.Flags().String("db", "", "assign db path")
	viper.BindPFlag("db", migrateUpCmd.Flags().Lookup("db"))

	migrateDownCmd.Flags().String("db", "", "assign db path")
	viper.BindPFlag("db", migrateDownCmd.Flags().Lookup("db"))
}
