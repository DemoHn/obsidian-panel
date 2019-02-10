package main

import (
	"os"

	"github.com/DemoHn/obsidian-panel/app"
	"github.com/spf13/cobra"
)

// flags
var configPath string

var rootCmd = &cobra.Command{
	Use:     "obs",
	Short:   "obsidian-panel main command",
	Long:    "obsidian-panel main command",
	Version: "0.7.0",
	Run: func(cmd *cobra.Command, args []string) {
		app.Init(configPath, false)
	},
	SilenceUsage: true,
}

func main() {
	if err := rootCmd.Execute(); err != nil {
		os.Exit(1)
	}
}

func init() {
	rootCmd.PersistentFlags().StringVarP(&configPath, "config", "c", "config.yml", "config path")
}
