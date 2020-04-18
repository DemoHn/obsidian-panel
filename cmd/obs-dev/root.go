package main

import (
	"os"

	"github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
	Use:          "obs-dev",
	Short:        "dev helper for obsidian-panel",
	SilenceUsage: true,
}

func main() {
	if err := rootCmd.Execute(); err != nil {
		os.Exit(1)
	}
}

func init() {
	rootCmd.AddCommand(migrateNewCmd)
	// migrate
	rootCmd.AddCommand(migrateUpCmd)
	rootCmd.AddCommand(migrateDownCmd)
	// http
	rootCmd.AddCommand(httpGetCmd)
	rootCmd.AddCommand(httpPostCmd)
	rootCmd.AddCommand(initCmd)
}
