package main

import (
	"fmt"
	"os"

	"github.com/DemoHn/obsidian-panel/cmd/obs/account"
	"github.com/DemoHn/obsidian-panel/cmd/obs/apm"

	"github.com/DemoHn/obsidian-panel/app"
	"github.com/spf13/cobra"
)

// flags
var configPath string

var rootCmd = &cobra.Command{
	Use:     "obs",
	Short:   "obsidian-panel main command",
	Version: "0.7.0",
	Run: func(cmd *cobra.Command, args []string) {
		app.GetProviders(configPath, false)
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
	rootCmd.AddCommand(account.AccountCmd)
	rootCmd.AddCommand(apm.ApmCmd)
	rootCmd.PersistentFlags().StringVarP(&configPath, "config", "c", "", "config filepath")
}
