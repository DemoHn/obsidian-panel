package main

import (
	"fmt"
	"os"

	"github.com/DemoHn/obsidian-panel/cmd/obs/account"
	"github.com/DemoHn/obsidian-panel/cmd/obs/apm"

	"github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
	Use:     "obs",
	Short:   "obsidian-panel main command",
	Version: "0.7.0",
	Run: func(cmd *cobra.Command, args []string) {
		//app.GetProviders(configPath, false)
		// TODO: add server init script
		fmt.Println("Hello World!")
	},
	SilenceUsage: true,
}

func main() {
	if err := rootCmd.Execute(); err != nil {
		os.Exit(1)
	}
}

func init() {
	// add sub-command
	rootCmd.AddCommand(account.RootCmd)
	rootCmd.AddCommand(apm.RootCmd)

	// add flags
	rootCmd.PersistentFlags().StringP("config", "c", "", "config filepath")
	rootCmd.PersistentFlags().BoolP("debug", "d", true, "debug mode")
}
